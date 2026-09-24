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
    def _old_body(store,path):
        """The content to restore, or None when the path did not exist."""
        if not store.exists(path):return None
        return store.read_file(path) if store.isfile(path) else None
    def _missing_dirs(store,path):
        """Directories ``makedirs`` will create, shallowest first (undos run in reverse)."""
        out=[];seen=""
        for name in path.strip("/").split("/"):
            seen=seen+"/"+name
            if not store.exists(seen):out.append(seen)
        return out
    def fs_write(h,p,data,overwrite=True):
        c=_cap(h,"fs","write");target=_vpath(c,p);raw=data.encode() if isinstance(data,str) else bytes(data)
        old=_old_body(c.target,target);b.charge_write(len(raw))
        runtime.journal(c,"write",path=target,body=old)
        c.target.write_file(target,raw);return len(raw)
    def fs_append(h,p,data):
        c=_cap(h,"fs","write");target=_vpath(c,p);raw=data.encode() if isinstance(data,str) else bytes(data)
        old=_old_body(c.target,target);b.charge_write(len(raw))
        runtime.journal(c,"write",path=target,body=old)
        c.target.append_file(target,raw);return len(raw)
    def fs_copy(sh,sp,dh,dp,overwrite=False):
        data=fs_read(sh,sp);c=_cap(dh,"fs","write");target=_vpath(c,dp)
        if not overwrite and c.target.exists(target):raise RuntimeError(f"目标已存在: {dp}")
        old=_old_body(c.target,target);b.charge_write(len(data))
        runtime.journal(c,"write",path=target,body=old)
        c.target.write_file(target,data);return len(data)
    def fs_mkdir(h,p,parents=False,mode=0o755):
        c=_cap(h,"fs","write");target=_vpath(c,p)
        if parents:
            for created in _missing_dirs(c.target,target):runtime.journal(c,"mkdir",path=created)
            c.target.makedirs(target,mode)
        else:
            runtime.journal(c,"mkdir",path=target);c.target.mkdir(target,mode)
    def fs_remove(h,p,recursive=False):
        c=_cap(h,"fs","delete");target=_vpath(c,p)
        try:info=c.target.lstat(target)
        except Exception:raise RuntimeError(f"路径不存在: {p}")
        if info.is_dir:
            # A tree cannot be reconstructed from its path, so it is copied aside
            # first; a file only needs its content.
            runtime.journal(c,"restore_tree" if recursive else "remove",path=target)
            c.target.rmtree(target) if recursive else c.target.rmdir(target)
        elif info.is_symlink:
            runtime.journal(c,"symlink",path=target,link_target=c.target.readlink(target))
            c.target.remove(target)
        else:
            runtime.journal(c,"write",path=target,body=c.target.read_file(target))
            c.target.remove(target)
    def fs_move(h,a,z):
        c=_cap(h,"fs","write");src=_vpath(c,a);dst=_vpath(c,z)
        if c.target.exists(dst):runtime.journal(c,"write",path=dst,body=_old_body(c.target,dst))
        runtime.journal(c,"rename",path=dst,to=src)
        c.target.rename(src,dst)
    def fs_link(h,a,z):
        c=_cap(h,"fs","write");src=_vpath(c,a);dst=_vpath(c,z)
        runtime.journal(c,"remove",path=dst)
        c.target.link(src,dst)
    def fs_symlink(h,target,p):
        c=_cap(h,"fs","write");dst=_vpath(c,p)
        runtime.journal(c,"remove",path=dst)
        c.target.symlink(str(target),dst)
    def fs_truncate(h,p,size):
        c=_cap(h,"fs","write");target=_vpath(c,p);size=int(size)
        runtime.journal(c,"write",path=target,body=_old_body(c.target,target))
        c.target.truncate(target,size)
    def fs_chmod(h,p,mode,follow=True):
        c=_cap(h,"fs","write");target=_vpath(c,p);mode=int(mode)
        info=c.target.stat(target,follow=follow)
        runtime.journal(c,"meta",path=target,mode=info.mode&0o7777,follow=follow)
        c.target.chmod(target,mode,follow)
    def fs_chown(h,p,uid=-1,gid=-1,follow=True):
        c=_cap(h,"fs","admin");target=_vpath(c,p)
        info=c.target.stat(target,follow=follow)
        runtime.journal(c,"meta",path=target,uid=info.uid,gid=info.gid,follow=follow)
        c.target.chown(target,int(uid),int(gid),follow)
    def fs_utime(h,p,atime=-1,mtime=-1,follow=True):
        c=_cap(h,"fs","write");target=_vpath(c,p)
        info=c.target.stat(target,follow=follow)
        runtime.journal(c,"meta",path=target,atime=info.atime,mtime=info.mtime,follow=follow)
        c.target.utime(target,int(atime),int(mtime),follow)
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
      "mkdir":fs_mkdir,"remove":fs_remove,"move":fs_move,"link":fs_link,"symlink":fs_symlink,"truncate":fs_truncate,
      "chmod":fs_chmod,"chown":fs_chown,"utime":fs_utime,
      "stat":lambda h,p:_stat_dict(_cap(h,"fs","read").target.stat(_vpath(h.cap,p))),"df":lambda h:_cap(h,"fs","read").target.df(),"du":lambda h,p="/":_cap(h,"fs","read").target.du(_vpath(h.cap,p)),"fsck":lambda h,repair=False:_cap(h,"fs","admin" if repair else "read").target.fsck(repair),
      "readlink":lambda h,p:_cap(h,"fs","read").target.readlink(_vpath(h.cap,p)),
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
