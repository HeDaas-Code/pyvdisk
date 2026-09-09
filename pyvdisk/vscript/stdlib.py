"""Capability-confined native standard library for VScript."""
from __future__ import annotations
import fnmatch, json, os, posixpath, time
from typing import Any,Dict
from .errors import CapabilityError,RuntimeError
from .policy import Capability
from .host import create_host_module

class NativeFunction:
    def __init__(self,name,fn):self.name=name;self.fn=fn
    def __call__(self,*args,**kwargs):return self.fn(*args,**kwargs)
    def __repr__(self):return f"<native {self.name}>"

class NativeModule:
    def __init__(self,name,members):self.name=name;self.members=members
    def member(self,name):
        if name.startswith("_") or name not in self.members:raise RuntimeError(f"模块 {self.name} 没有成员 {name}")
        return self.members[name]

class Handle:
    def __init__(self,cap:Capability):self.cap=cap
    @property
    def kind(self):return self.cap.kind
    @property
    def name(self):return self.cap.name
    def __repr__(self):return f"<{self.cap.kind} mount {self.cap.name}>"

def _cap(handle,kind,*permissions):
    if not isinstance(handle,Handle) or handle.cap.kind!=kind:raise CapabilityError(f"需要 {kind} 磁盘句柄")
    handle.cap.require(*permissions);return handle.cap

def _vpath(cap,path):
    raw=str(path).replace("\\","/")
    if "\x00" in raw:raise CapabilityError("路径包含 NUL")
    parts=[]
    for p in raw.split("/"):
        if p in ("","."):continue
        if p=="..":
            if not parts:raise CapabilityError("路径越出授权根目录")
            parts.pop()
        else:parts.append(p)
    root=cap.root.rstrip("/") or "/";joined=posixpath.join(root,*parts)
    if not (joined==root or joined.startswith(root.rstrip("/")+"/")):raise CapabilityError("路径越出授权根目录")
    return joined

def create_stdlib(runtime):
    b=runtime.budget
    def fs_read(h,p):
        c=_cap(h,"fs","read");data=c.target.read_file(_vpath(c,p));b.charge_read(len(data));return data
    def fs_read_text(h,p,encoding="utf-8"):return fs_read(h,p).decode(encoding)
    def fs_write(h,p,data,overwrite=True):
        c=_cap(h,"fs","write");target=_vpath(c,p);raw=data.encode() if isinstance(data,str) else bytes(data);existed=c.target.exists(target);old=c.target.read_file(target) if existed and c.target.isfile(target) else None;b.charge_write(len(raw));c.target.write_file(target,raw)
        runtime.record_operation({"kind":"write","path":target,"old":old.decode("latin1") if old is not None else None,"new":raw.decode("latin1")})
        runtime.record_undo(lambda: c.target.write_file(target,old) if existed and old is not None else (c.target.remove(target) if c.target.exists(target) else None));return len(raw)
    def fs_append(h,p,data):
        c=_cap(h,"fs","write");target=_vpath(c,p);raw=data.encode() if isinstance(data,str) else bytes(data);existed=c.target.exists(target);old=c.target.read_file(target) if existed else None;b.charge_write(len(raw));c.target.append_file(target,raw)
        runtime.record_operation({"kind":"append","path":target,"old":old.decode("latin1") if old is not None else None,"new":raw.decode("latin1")})
        runtime.record_undo(lambda: c.target.write_file(target,old) if existed else c.target.remove(target));return len(raw)
    def fs_copy(sh,sp,dh,dp,overwrite=False):
        data=fs_read(sh,sp);c=_cap(dh,"fs","write");target=_vpath(c,dp)
        if not overwrite and c.target.exists(target):raise RuntimeError(f"目标已存在: {dp}")
        b.charge_write(len(data));c.target.write_file(target,data);return len(data)
    def _stat_dict(s):
        return {"ino":s.ino,"type":s.type,"mode":s.mode,"nlink":s.nlink,"size":s.size,"uid":s.uid,"gid":s.gid,"atime":s.atime,"mtime":s.mtime,"ctime":s.ctime,"is_file":s.is_file,"is_dir":s.is_dir,"is_symlink":s.is_symlink}
    def fs_walk(h,p="/"):
        c=_cap(h,"fs","read"); return [(top,list(dirs),list(files)) for top,dirs,files in c.target.walk(_vpath(c,p))]
    def fs_glob(h,pattern,root="/"):
        c=_cap(h,"fs","read"); out=[]
        for top,dirs,files in c.target.walk(_vpath(c,root)):
            for name in list(dirs)+list(files):
                path=posixpath.join(top,name)
                if fnmatch.fnmatch(path,str(pattern)) or fnmatch.fnmatch(path.lstrip("/"),str(pattern)): out.append(path)
        return sorted(out)
    def fs_listdir_with_stat(h,p="/"):
        c=_cap(h,"fs","read"); return [{"name":n,"stat":_stat_dict(s)} for n,s in c.target.listdir_with_stat(_vpath(c,p))]
    fs={
      "exists":lambda h,p:_cap(h,"fs","read").target.exists(_vpath(h.cap,p)),"is_file":lambda h,p:_cap(h,"fs","read").target.isfile(_vpath(h.cap,p)),"is_dir":lambda h,p:_cap(h,"fs","read").target.isdir(_vpath(h.cap,p)),
      "list":lambda h,p="/":sorted(_cap(h,"fs","read").target.listdir(_vpath(h.cap,p))),"listdir":lambda h,p="/":sorted(_cap(h,"fs","read").target.listdir(_vpath(h.cap,p))),"listdir_with_stat":fs_listdir_with_stat,"walk":fs_walk,"glob":fs_glob,
      "read":fs_read,"read_text":fs_read_text,"write":fs_write,"append":fs_append,"copy":fs_copy,
      "mkdir":lambda h,p,parents=False,mode=0o755:(_cap(h,"fs","write").target.makedirs(_vpath(h.cap,p),mode) if parents else _cap(h,"fs","write").target.mkdir(_vpath(h.cap,p),mode)),"remove":lambda h,p,recursive=False:(_cap(h,"fs","delete").target.rmtree(_vpath(h.cap,p)) if recursive else _cap(h,"fs","delete").target.remove(_vpath(h.cap,p))),"move":lambda h,a,z:_cap(h,"fs","write").target.rename(_vpath(h.cap,a),_vpath(h.cap,z)),
      "stat":lambda h,p:_stat_dict(_cap(h,"fs","read").target.stat(_vpath(h.cap,p))),"df":lambda h:_cap(h,"fs","read").target.df(),"du":lambda h,p="/":_cap(h,"fs","read").target.du(_vpath(h.cap,p)),"fsck":lambda h,repair=False:_cap(h,"fs","admin" if repair else "read").target.fsck(repair),
      "chmod":lambda h,p,mode,follow=True:_cap(h,"fs","write").target.chmod(_vpath(h.cap,p),int(mode),follow),"chown":lambda h,p,uid=-1,gid=-1,follow=True:_cap(h,"fs","admin").target.chown(_vpath(h.cap,p),int(uid),int(gid),follow),"utime":lambda h,p,atime=-1,mtime=-1,follow=True:_cap(h,"fs","write").target.utime(_vpath(h.cap,p),int(atime),int(mtime),follow),"truncate":lambda h,p,size:_cap(h,"fs","write").target.truncate(_vpath(h.cap,p),int(size)),"link":lambda h,a,z:_cap(h,"fs","write").target.link(_vpath(h.cap,a),_vpath(h.cap,z)),"symlink":lambda h,target,p:_cap(h,"fs","write").target.symlink(str(target),_vpath(h.cap,p)),"readlink":lambda h,p:_cap(h,"fs","read").target.readlink(_vpath(h.cap,p)),
    }
    vec={
      "collections":lambda h:_cap(h,"vector","read").target.list_collections(),
      "create_collection":lambda h,n,d,metric="cosine",max_elements=10000:_cap(h,"vector","schema").target.create_collection(n,d,metric,max_elements),
      "drop_collection":lambda h,n:_cap(h,"vector","schema").target.drop_collection(n),
      "upsert":lambda h,c,i,v,metadata=None:_cap(h,"vector","mutate").target.upsert(c,str(i),v,metadata or {}),
      "upsert_many":lambda h,c,items:_cap(h,"vector","mutate").target.upsert_many(c,items),
      "get":lambda h,c,i:_cap(h,"vector","read").target.get(c,str(i)),
      "delete":lambda h,c,i:_cap(h,"vector","mutate").target.delete(c,str(i)),
      "count":lambda h,c:_cap(h,"vector","read").target.count(c),
      "search":lambda h,c,q,k=10,where=None:_cap(h,"vector","query").target.search(c,q,k,where),
    }
    def log_emit(h,s,level,logger,message,fields=None,tags=None,timestamp_ns=None):
        c=_cap(h,"log","append"); kw={"level":level,"logger":logger,"message":message,"fields":fields or {},"tags":tags or {}}
        if timestamp_ns is not None: kw["timestamp_ns"]=int(timestamp_ns)
        return c.target.append(s,**kw).to_dict()
    logs={
      "streams":lambda h:_cap(h,"log","query").target.list_streams(),
      "create_stream":lambda h,n,segment_events=1000,retention_seconds=None,max_events=None:_cap(h,"log","schema").target.create_stream(n,segment_events,retention_seconds,max_events),
      "drop_stream":lambda h,n:_cap(h,"log","schema").target.drop_stream(n),
      "emit":log_emit,
      "emit_many":lambda h,s,events:[e.to_dict() for e in _cap(h,"log","append").target.append_many(s,events)],
      "count":lambda h,s,**kw:_cap(h,"log","query").target.count(s,**kw),
      "query":lambda h,s,**kw:[e.to_dict() for e in _cap(h,"log","query").target.query(s,**kw)],
      "tail":lambda h,s,count=100,**kw:[e.to_dict() for e in _cap(h,"log","query").target.tail(s,count,**kw)],
      "stats":lambda h,s:_cap(h,"log","query").target.stats(s),
      "compact":lambda h,s:_cap(h,"log","compact").target.compact(s),
      "retention":lambda h,s:_cap(h,"log","retention").target.enforce_retention(s),
    }
    modules={"fs":NativeModule("fs",{k:NativeFunction("fs."+k,v) for k,v in fs.items()}),
            "vector":NativeModule("vector",{k:NativeFunction("vector."+k,v) for k,v in vec.items()}),
            "log":NativeModule("log",{k:NativeFunction("log."+k,v) for k,v in logs.items()}),
            "json":NativeModule("json",{"encode":NativeFunction("json.encode",lambda v,indent=None:json.dumps(v,ensure_ascii=False,indent=indent)),"decode":NativeFunction("json.decode",json.loads)}),
            "time":NativeModule("time",{"now_ns":NativeFunction("time.now_ns",time.time_ns),"sleep":NativeFunction("time.sleep",lambda seconds:time.sleep(float(seconds)))}),}
    modules["host"]=create_host_module(runtime)
    return modules
