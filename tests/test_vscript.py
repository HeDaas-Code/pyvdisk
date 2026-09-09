import io
import tempfile
import unittest
from pathlib import Path
from pyvdisk.vscript import Compiler, Runtime, Policy, Capability, Handle
from pyvdisk.vscript.errors import LexError, ParseError, RuntimeError, CapabilityError, ResourceLimitError
from pyvdisk.vscript.lexer import lex

class FakeFS:
    def __init__(self):self.files={}
    def write_file(self,p,d):self.files[p]=d
    def read_file(self,p):return self.files[p]
    def append_file(self,p,d):self.files[p]=self.files.get(p,b"")+d
    def remove(self,p):del self.files[p]
    def exists(self,p):return p in self.files or p=="/"
    def isfile(self,p):return p in self.files
    def isdir(self,p):return p=="/"
    def listdir(self,p):return sorted(x[1:] for x in self.files)
    def mkdir(self,*a):return None
    def makedirs(self,*a):return None
    def df(self):return {"total_bytes":1}
    def du(self,p):return sum(map(len,self.files.values()))
    def fsck(self,repair=False):return {"ok":True}

class VScriptTests(unittest.TestCase):
    def run_script(self,s,**kw):
        out=io.StringIO();p=Compiler().compile(s);r=Runtime(stdout=out,policy=kw.pop("policy",None));result=r.run(p.ast,**kw);return result,out.getvalue(),r
    def test_lexer_literals_comments(self):
        ts=lex('/* a /* b */ c */ let x=0xff; let y=1.5e2;')
        self.assertEqual(ts[3].value,255);self.assertEqual(ts[8].value,150.0)
    def test_bad_lex_and_parse(self):
        with self.assertRaises(LexError):lex('"x')
        with self.assertRaises(ParseError):Compiler().compile('language "1.0"; let x=;')
    def test_language_extensions(self):
        self.run_script('language "1.0"; let inc=fn(x)->x+1; assert inc(2)==3; let twice=|x| x*2; assert twice(3)==6; let n=2; match n { 1 => { assert false; } 2 => { assert true; } }')
        self.run_script('language "1.0"; let n=2 |> int; assert n==2; let raw=r"a\\n"; assert raw=="a\\\\n"; let data=b"a"; assert data.length==1;')

    def test_transaction_rollback(self):
        fs=FakeFS();h=Handle(Capability("d","fs",frozenset({"read","write"}),fs,"/"))
        self.run_script('language "1.0"; fs.write(d,"/x","old"); try { transaction { fs.write(d,"/x","new"); throw "fail"; } on rollback { } } catch(e) { } assert fs.read_text(d,"/x")=="old";',bindings={"d":h})

    def test_nested_transaction_commit_merges_undo_log(self):
        fs=FakeFS();h=Handle(Capability("d","fs",frozenset({"read","write"}),fs,"/"))
        script='''language "1.0";
fs.write(d,"/x","before");
try { transaction {
  fs.write(d,"/x","outer");
  transaction { fs.write(d,"/x","inner"); }
  throw "abort outer";
} } catch(e) { }
assert fs.read_text(d,"/x")=="before";'''
        self.run_script(script,bindings={"d":h})

    def test_nested_transaction_failure_isolated_when_caught(self):
        fs=FakeFS();h=Handle(Capability("d","fs",frozenset({"read","write"}),fs,"/"))
        script='''language "1.0";
try { transaction {
  fs.write(d,"/outer","kept");
  try { transaction { fs.write(d,"/inner","discarded"); throw "inner"; } }
  catch(e) { assert fs.exists(d,"/inner")==false; }
  assert fs.read_text(d,"/outer")=="kept";
} } catch(e) { assert false; }
assert fs.read_text(d,"/outer")=="kept";
assert fs.exists(d,"/inner")==false;'''
        self.run_script(script,bindings={"d":h})

    def test_rollback_handler_runs_after_undo(self):
        fs=FakeFS();h=Handle(Capability("d","fs",frozenset({"read","write"}),fs,"/"))
        script='''language "1.0";
let handler_ran=false;
fs.write(d,"/x","original");
try { transaction { fs.write(d,"/x","changed"); throw "fail"; }
  on rollback { handler_ran=true; assert fs.read_text(d,"/x")=="original"; }
} catch(e) { assert handler_ran; }
assert fs.read_text(d,"/x")=="original";'''
        self.run_script(script,bindings={"d":h})

    def test_fs_write_and_append_restore_existing_and_new_files(self):
        fs=FakeFS();fs.files["/existing"]=b"seed"
        h=Handle(Capability("d","fs",frozenset({"read","write"}),fs,"/"))
        script='''language "1.0";
try { transaction {
  fs.write(d,"/existing","replaced");
  fs.append(d,"/existing","+more");
  fs.write(d,"/new","created");
  fs.append(d,"/new-append","tail");
  throw "fail";
} } catch(e) { }
assert fs.read_text(d,"/existing")=="seed";
assert fs.exists(d,"/new")==false;
assert fs.exists(d,"/new-append")==false;'''
        self.run_script(script,bindings={"d":h})

    def test_parallel_tasks(self):
        script='language "1.0"; parallel { task first { return 2 + 3; } task second { return 4 * 5; } } assert await first == 5; assert await second == 20;'
        self.run_script(script)

    def test_parallel_task_limit(self):
        with self.assertRaises(ResourceLimitError): self.run_script('language "1.0"; parallel { task a { return 1; } task b { return 2; } }',policy=Policy(max_tasks=1))

    def test_await_propagates_task_failure(self):
        script = 'language "1.0"; parallel { task broken { return 1 / 0; } } await broken;'
        with self.assertRaises(RuntimeError): self.run_script(script)

    def test_math_control_function(self):
        s='language "1.0"; fn add(a,b){return a+b;} let x=0; for i in 1..=5 { if i==3 {continue;} x+=i;} assert x==12; assert add(2,3)==5; print(x);'
        _,out,_=self.run_script(s);self.assertEqual(out,"12\n")
    def test_try_throw(self):
        self.run_script('language "1.0"; let ok=false; try {throw "x";} catch(e) {ok=true;} finally {assert true;} assert ok;')
    def test_resource_limit(self):
        with self.assertRaises(ResourceLimitError):self.run_script('language "1.0"; while true {}',policy=Policy(max_steps=20,max_loop_iterations=1000))
    def test_fs_capability(self):
        fs=FakeFS();h=Handle(Capability("d","fs",frozenset({"read","write"}),fs,"/"))
        self.run_script('language "1.0"; fs.write(d,"/x","hi"); fs.append(d,"/x","!"); assert fs.read_text(d,"/x")=="hi!";',bindings={"d":h})
    def test_readonly_denied(self):
        h=Handle(Capability("d","fs",frozenset({"read"}),FakeFS(),"/"))
        with self.assertRaises(CapabilityError):self.run_script('language "1.0"; fs.write(d,"/x","hi");',bindings={"d":h})
    def test_private_member_denied(self):
        with self.assertRaises(RuntimeError):self.run_script('language "1.0"; let x={"a":1}; x.__class__;')
    def test_module_export_import(self):
        from pyvdisk.vscript import run_file
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"lib.vds").write_text('language "1.0"; export fn inc(x){ return x+1; }')
            main=root/"main.vds"; main.write_text('language "1.0"; import "./lib.vds" as lib; assert lib.inc(2)==3;')
            run_file(main, module_roots=[root])
    def test_module_path_is_restricted(self):
        from pyvdisk.vscript import run_file
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); main=root/"main.vds"; main.write_text('language "1.0"; import "../../etc/passwd" as x;')
            with self.assertRaises(Exception): run_file(main, module_roots=[root])
    def test_extension_and_version(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.txt";p.write_text('language "1.0";')
            with self.assertRaises(Exception):Compiler().compile_file(p)
        with self.assertRaises(Exception):Compiler().compile('language "2.0";')


class VScriptEndToEndTests(unittest.TestCase):
    def execute(self,source,args,allowed):
        from pyvdisk.vscript import MountRegistry
        out=io.StringIO()
        with MountRegistry() as mounts:
            runtime=Runtime(stdout=out,mount_registry=mounts,allowed_mounts=allowed)
            runtime.run(Compiler().compile(source).ast,args=args)
        return out.getvalue()
    def test_real_fs_vector_log_disks(self):
        from pyvdisk.vfs import VFS
        from pyvdisk.vector_disk import VectorDisk
        from pyvdisk.log_disk import LogDisk
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fs_path=root/"files.vdisk";vec_path=root/"vectors.vdisk";log_path=root/"logs.vdisk"
            VFS.create(str(fs_path),8*1024*1024)
            VectorDisk.create(str(vec_path),16*1024*1024)
            LogDisk.create(str(log_path),8*1024*1024)
            script='''language "1.0";
import std.fs as fs; import std.vector as vector; import std.log as log;
require { mount docs: fs read, write; mount embeddings: vector read, query, mutate, schema; mount audit: log query, append, schema, compact; }
mount fs docs from arg("docs"); mount vector embeddings from arg("vectors"); mount log audit from arg("logs");
fs.write(docs,"/hello.txt","hello vscript"); assert fs.read_text(docs,"/hello.txt")=="hello vscript"; assert fs.stat(docs,"/hello.txt").size==13;
vector.create_collection(embeddings,"docs",3); vector.upsert(embeddings,"docs","a",[1.0,0.0,0.0],metadata:{"kind":"news"}); assert vector.count(embeddings,"docs")==1; let hits=vector.search(embeddings,"docs",[1.0,0.0,0.0],k:1); assert hits[0].id=="a";
log.create_stream(audit,"app",segment_events:2); log.emit(audit,"app","INFO","e2e","done",fields:{"ok":true}); assert log.stats(audit,"app").events==1; assert log.tail(audit,"app",count:1)[0].message=="done"; print("e2e-ok");'''
            args={"docs":str(fs_path),"vectors":str(vec_path),"logs":str(log_path)}
            allowed={str(fs_path):{"read","write"},str(vec_path):{"read","query","mutate","schema"},str(log_path):{"query","append","schema","compact"}}
            self.assertEqual(self.execute(script,args,allowed),"e2e-ok\n")
            with VFS(str(fs_path)) as mounted:self.assertEqual(mounted.read_file("/hello.txt"),b"hello vscript")
            with VectorDisk(str(vec_path)) as mounted:self.assertEqual(mounted.count("docs"),1)
            with LogDisk(str(log_path)) as mounted:self.assertEqual(mounted.stats("app")["events"],1)
    def test_script_mount_permission_intersection(self):
        from pyvdisk.vfs import VFS
        from pyvdisk.vscript import MountRegistry
        with tempfile.TemporaryDirectory() as td:
            path=str(Path(td)/"disk.vdisk");VFS.create(path,8*1024*1024)
            source='language "1.0"; require { mount d: fs read, write; } mount fs d from arg("d");'
            with MountRegistry() as mounts:
                runtime=Runtime(mount_registry=mounts,allowed_mounts={path:{"read"}})
                with self.assertRaises(CapabilityError):runtime.run(Compiler().compile(source).ast,args={"d":path})
    def test_run_disk_cli(self):
        from contextlib import redirect_stdout,redirect_stderr
        from pyvdisk.vfs import VFS
        from pyvdisk.cli import main
        with tempfile.TemporaryDirectory() as td:
            path=str(Path(td)/"disk.vdisk");VFS.create(path,8*1024*1024)
            source='language "1.0"; import std.fs as fs; require { mount self: fs read; } mount fs self from arg("self"); assert fs.exists(self,"/"); print("disk-ok");'
            with VFS(path) as mounted:mounted.makedirs("/.vscript/scripts");mounted.write_file("/.vscript/scripts/job.vds",source.encode())
            out=io.StringIO();err=io.StringIO()
            with redirect_stdout(out),redirect_stderr(err):code=main(["vscript","run-disk",path+":/.vscript/scripts/job.vds"])
            self.assertEqual(code,0,err.getvalue());self.assertIn("disk-ok",out.getvalue())