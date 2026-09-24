"""Command-line frontend for the VScript MVP."""
from __future__ import annotations
import sys
from . import Compiler, Runtime, MountRegistry
from .policy import Policy
from .runtime import recover_wal
from .wal import WriteAheadLog
from .errors import VScriptError, CapabilityError, ResourceLimitError, LexError, ParseError, CompileError

def _pairs(values):
    result={}
    for item in values or []:
        if "=" not in item: raise ValueError(f"参数必须为 KEY=VALUE: {item}")
        key,value=item.split("=",1);result[key]=value
    return result

def _policy(args):
    """Build the runtime policy, including the host roots the CLI was given.

    ``host.*`` is a confined bridge to the *host* filesystem; a policy that never
    names a root grants nothing, so these switches are the only way to turn it on.
    """
    return Policy(host_read_roots=list(getattr(args,"host_read_root",None) or []),
                  host_write_roots=list(getattr(args,"host_write_root",None) or []))

def _mounts(values,registry):
    bindings={};allowed={}
    for item in values or []:
        parts=item.split(":",2)
        if len(parts)==2:
            path,raw=parts;allowed[path]=set(raw.split(","));continue
        if len(parts)!=3: raise ValueError("挂载格式为 PATH:PERM[,PERM] 或 NAME:PATH:PERM[,PERM]")
        name,path,raw=parts;perms=set(raw.split(","));bindings[name]=registry.open(name,path,permissions=perms);allowed[path]=perms
    return bindings,allowed

def _recovery_mounts(bindings):
    """Map a pre-bound mount name to the capability its operations were recorded against."""
    out={}
    for name,handle in (bindings or {}).items():
        cap=getattr(handle,"cap",None)
        if cap is not None and cap.kind=="fs": out[name]=cap.target
    return out

def command(args):
    try:
        if args.action=="check":Compiler().compile_file(args.script);print(f"OK: {args.script}");return 0
        if args.action=="repl":return repl(_policy(args))
        if args.action=="run-disk":
            if ":" not in args.location:raise ValueError("run-disk 位置应为 DISK.vdisk:/path.vds")
            disk_path,vpath=args.location.split(":",1)
            from ..vfs import VFS
            with VFS(disk_path) as bootstrap:source=bootstrap.read_file(vpath).decode("utf-8")
            program=Compiler().compile(source,args.location)
            args.arg=list(args.arg)+[f"self={disk_path}"]
            args.mount=list(args.mount)+[f"{disk_path}:read"]
        else:program=Compiler().compile_file(args.script)
        with MountRegistry() as mounts:
            bindings,allowed=_mounts(args.mount,mounts)
            # A transaction log is recovered before the script runs and settled after it,
            # so a killed process cannot leave a half-applied transaction behind.
            wal=WriteAheadLog(args.wal) if getattr(args,"wal",None) else None
            unresolved=0
            if wal is not None:
                report=recover_wal(wal,_recovery_mounts(bindings))
                unresolved=len(report["unresolved"])
                if report["pending"]: print(f"恢复: 回滚 {len(report['pending'])} 个未完成事务（{report['rolled_back']} 次写入被撤销）",file=sys.stderr)
                if report["deferred"]: print(f"恢复: {len(report['deferred'])} 个未完成事务因挂载缺失未能回滚，日志保留",file=sys.stderr)
            runtime=Runtime(policy=_policy(args),stdout=sys.stdout,mount_registry=mounts,allowed_mounts=allowed,wal=wal)
            try:
                runtime.run(program.ast,args=_pairs(args.arg),bindings=bindings)
            finally:
                if wal is not None and not unresolved and not runtime.transactions_open():
                    _,pending=wal.recover()
                    if not pending: wal.truncate()
        return 0
    except (LexError,ParseError,CompileError) as e:print(e,file=sys.stderr);return 2
    except CapabilityError as e:print(e,file=sys.stderr);return 3
    except ResourceLimitError as e:print(e,file=sys.stderr);return 5
    except VScriptError as e:print(e,file=sys.stderr);return 4
    except (OSError,ValueError) as e:print(e,file=sys.stderr);return 4

def _repl_source(source):
    """Add the language header and a terminator suitable for a REPL snippet."""
    source = source.strip()
    if not source:
        return 'language "1.0";\n'
    return 'language "1.0";\n' + source + ("" if source.endswith((";", "}")) else ";") + "\n"


def _repl_type(value):
    """Return the stable, user-facing VScript type name for a value."""
    if value is None:
        return "Null"
    if isinstance(value, bool):
        return "Bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "Int"
    if isinstance(value, float):
        return "Float"
    if isinstance(value, str):
        return "String"
    if isinstance(value, list):
        return "List"
    if isinstance(value, dict):
        return "Map"
    return type(value).__name__


def _repl_help():
    print("REPL commands:")
    print("  :limits             show runtime resource limits")
    print("  :mounts             show mounted capabilities")
    print("  :type NAME          show the type and value of a name")
    print("  :ast SOURCE         compile SOURCE and show its AST")
    print("  :help               show this help")
    print("  :reset              reset the runtime environment")
    print("  :quit (:q)          leave the REPL")


def repl(policy=None):
    # Keep one Runtime alive: definitions, functions, task state, and imports
    # therefore survive from one input line to the next.  MountRegistry is kept
    # alongside it so handles remain valid for the lifetime of the session.
    with MountRegistry() as mounts:
        runtime = Runtime(policy=policy, stdout=sys.stdout, mount_registry=mounts)
        _repl_help()
        while True:
            try:
                line = input("vscript> ")
            except EOFError:
                break
            line = line.strip()
            if not line:
                continue
            if line in (":quit", ":q"):
                break
            if line == ":help":
                _repl_help()
                continue
            if line == ":reset":
                # Closing the old registry releases any disk handles before
                # replacing both pieces of session state.
                mounts.close()
                mounts = MountRegistry()
                runtime = Runtime(policy=policy, stdout=sys.stdout, mount_registry=mounts)
                print("Runtime reset.")
                continue
            if line == ":limits":
                print(runtime.policy)
                continue
            if line == ":mounts":
                current = mounts.handles()
                if not current:
                    print("(no mounts)")
                else:
                    for name, handle in current.items():
                        print(f"{name}: {handle.kind} ({', '.join(sorted(handle.cap.permissions))})")
                continue
            if line.startswith(":type"):
                name = line[len(":type"):].strip()
                if not name or not name.isidentifier():
                    print("用法: :type NAME", file=sys.stderr)
                    continue
                try:
                    value = runtime.globals.get(name)
                    print(f"{name}: {_repl_type(value)} = {runtime.stringify(value)}")
                except VScriptError as e:
                    print(e, file=sys.stderr)
                continue
            if line.startswith(":ast"):
                snippet = line[len(":ast"):].strip()
                if not snippet:
                    print("用法: :ast SOURCE", file=sys.stderr)
                    continue
                try:
                    print(Compiler().compile(_repl_source(snippet)).ast)
                except VScriptError as e:
                    print(e, file=sys.stderr)
                continue
            try:
                program = Compiler().compile(_repl_source(line))
                runtime.run(program.ast)
            except VScriptError as e:
                print(e, file=sys.stderr)
    return 0

def add_parser(sub):
    root=sub.add_parser("vscript",help="运行安全 VScript 批处理脚本")
    actions=root.add_subparsers(dest="action",required=True)
    check=actions.add_parser("check",help="检查 .vds 语法");check.add_argument("script");check.set_defaults(func=command)
    run=actions.add_parser("run",help="执行 .vds 脚本");run.add_argument("script");run.add_argument("--arg",action="append",default=[]);run.add_argument("--mount",action="append",default=[],help="PATH:PERMS（授权）或 NAME:PATH:PERMS（预挂载）");run.add_argument("--wal",default=None,help="事务日志路径；启动时先恢复未完成事务，结束时结算并截断");run.add_argument("--host-read-root",action="append",default=[],help="允许 host.read/import_file 的宿主目录（可重复）");run.add_argument("--host-write-root",action="append",default=[],help="允许 host.write/export_file 的宿主目录（可重复）");run.set_defaults(func=command)
    disk=actions.add_parser("run-disk",help="执行普通 .vdisk 内的脚本");disk.add_argument("location");disk.add_argument("--arg",action="append",default=[]);disk.add_argument("--mount",action="append",default=[]);disk.add_argument("--wal",default=None,help="事务日志路径；启动时先恢复未完成事务，结束时结算并截断");disk.add_argument("--host-read-root",action="append",default=[],help="允许 host.read/import_file 的宿主目录（可重复）");disk.add_argument("--host-write-root",action="append",default=[],help="允许 host.write/export_file 的宿主目录（可重复）");disk.set_defaults(func=command)
    replp=actions.add_parser("repl",help="交互式 VScript");replp.add_argument("--host-read-root",action="append",default=[],help="允许 host.read/import_file 的宿主目录（可重复）");replp.add_argument("--host-write-root",action="append",default=[],help="允许 host.write/export_file 的宿主目录（可重复）");replp.set_defaults(func=command)
    return root
