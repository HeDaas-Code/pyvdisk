"""时序数据库风格的分段、追加式日志数据盘。"""
from __future__ import annotations
import hashlib, json, threading, time
from typing import Any, Dict, Iterable, Iterator, List, Optional
from .disk import VirtualDisk
from .identity import probe_disk, write_identity_to_block0
from .logging_core import LEVELS, LogEvent, normalize_level
from .vfs import VFS

LOG_ROOT="/.logs"; LOG_MANIFEST="/.log_disk.json"
class LogDiskError(Exception): pass

def _json(value): return json.dumps(value,ensure_ascii=False,separators=(",",":"))
def _match(value,where):
    if not where: return True
    merged=dict(value.get("fields") or {}); merged.update({"tags."+k:v for k,v in (value.get("tags") or {}).items()})
    merged.update({k:value.get(k) for k in ("level","logger","message","event_id","sequence","schema_version","run_id","task_id","correlation_id")})
    for key,cond in where.items():
        actual=merged.get(key)
        if not isinstance(cond,dict):
            if actual!=cond:return False
            continue
        for op,want in cond.items():
            try:
                if op=="$eq":ok=actual==want
                elif op=="$ne":ok=actual!=want
                elif op=="$gt":ok=actual>want
                elif op=="$gte":ok=actual>=want
                elif op=="$lt":ok=actual<want
                elif op=="$lte":ok=actual<=want
                elif op=="$in":ok=actual in want
                elif op=="$contains":ok=want in actual
                else:raise LogDiskError(f"不支持的过滤操作符: {op}")
            except TypeError:ok=False
            if not ok:return False
    return True

class LogDisk:
    """多流、分段、时间索引的结构化日志盘。"""
    def __init__(self,path): self.path=path; self.vfs=VFS(path); self._mounted=False; self._lock=threading.RLock()
    @staticmethod
    def create(path,size_bytes,label=""):
        VFS.create(path,size_bytes,label=label)
        with VFS(path) as v:
            v.makedirs(LOG_ROOT); v.write_file(LOG_MANIFEST,_json({"type":"log","version":1}).encode())
        ident=probe_disk(path); d=VirtualDisk(path); d.open()
        try: write_identity_to_block0(d,ident.disk_uuid,"",label,False,is_log=True)
        finally:d.close()
    def mount(self):
        if self._mounted:return self
        if probe_disk(self.path).kind!="log":raise LogDiskError(f"不是日志数据盘: {self.path}")
        self.vfs.mount()
        try:
            for dirname in self.vfs.listdir(LOG_ROOT):
                base=f"{LOG_ROOT}/{dirname}"; mp=base+"/manifest.json"
                if not self.vfs.exists(mp): continue
                man=self._read(mp); man.setdefault("schema_version",1); man.setdefault("consumers",{}); man.setdefault("event_ids",{})
                for seg in man.get("segments",[]):
                    path=base+"/"+seg["file"]
                    if not self.vfs.exists(path): raise LogDiskError("日志分段缺失")
                    checksum=hashlib.sha256(self.vfs.read_file(path)).hexdigest()
                    if seg.get("checksum") and seg["checksum"] != checksum: raise LogDiskError("日志分段校验失败")
                    seg["checksum"]=checksum
                self._write(mp,man)
        except Exception:
            self.vfs.close(); raise
        self._mounted=True; return self
    def close(self):
        if self._mounted:self.vfs.close();self._mounted=False
    def __enter__(self):return self.mount()
    def __exit__(self,*exc):self.close()
    def _need(self):
        if not self._mounted:raise LogDiskError("日志盘未挂载")
    @staticmethod
    def _key(name):
        if not name or "/" in name or "\\" in name:raise LogDiskError("流名不能为空或包含路径分隔符")
        return hashlib.sha256(name.encode()).hexdigest()[:24]
    def _dir(self,name):return f"{LOG_ROOT}/{self._key(name)}"
    def _read(self,path):return json.loads(self.vfs.read_file(path).decode())
    def _write(self,path,value):self.vfs.write_file(path,_json(value).encode())
    def create_stream(self,name,segment_events=1000,retention_seconds=None,max_events=None):
        with self._lock:
            self._need();base=self._dir(name)
            if self.vfs.exists(base):raise LogDiskError(f"日志流已存在: {name}")
            if segment_events<=0:raise LogDiskError("segment_events 必须为正数")
            self.vfs.mkdir(base);self.vfs.mkdir(base+"/segments")
            self._write(base+"/config.json",{"name":name,"segment_events":segment_events,"retention_seconds":retention_seconds,"max_events":max_events,"sequence":0,"schema_version":1})
            self._write(base+"/manifest.json",{"next_segment":0,"next_sequence":0,"segments":[],"schema_version":1,"consumers":{},"event_ids":{}})
    def list_streams(self):
        self._need();out=[]
        for d in self.vfs.listdir(LOG_ROOT):
            p=f"{LOG_ROOT}/{d}/config.json"
            if self.vfs.exists(p):
                c=self._read(p);c["count"]=sum(x["count"] for x in self._read(f"{LOG_ROOT}/{d}/manifest.json")["segments"]);out.append(c)
        return sorted(out,key=lambda x:x["name"])
    def drop_stream(self,name):
        with self._lock:self._config(name);self.vfs.rmtree(self._dir(name))
    def _config(self,name):
        self._need();p=self._dir(name)+"/config.json"
        if not self.vfs.exists(p):raise LogDiskError(f"日志流不存在: {name}")
        c=self._read(p)
        if c["name"]!=name:raise LogDiskError("日志流配置损坏")
        return c
    def append(self,stream,event=None,**kwargs):
        with self._lock:
            cfg=self._config(stream);base=self._dir(stream);man=self._read(base+"/manifest.json")
            if event is None:event=LogEvent(timestamp_ns=kwargs.pop("timestamp_ns",time.time_ns()),**kwargs)
            elif isinstance(event,dict):event=LogEvent.from_dict(event)
            if not isinstance(event,LogEvent):raise LogDiskError("event 必须是 LogEvent 或字典")
            # event_id is the durable idempotency key: retries return the
            # originally published event instead of allocating another sequence.
            known=man.setdefault("event_ids",{})
            if event.event_id in known:
                return LogEvent.from_dict(known[event.event_id])
            # Optional trace metadata may be supplied at append time without
            # changing the legacy event/return contract.
            for key in ("schema_version", "run_id", "task_id", "correlation_id"):
                if key in kwargs:
                    setattr(event, key, kwargs[key])
            # Lazily migrate streams created by older versions. The manifest is
            # the authoritative allocator; the lock makes allocation atomic.
            if "next_sequence" not in man:
                man["next_sequence"]=sum(s.get("count",0) for s in man.get("segments",[]))
            event.sequence=man["next_sequence"];man["next_sequence"]+=1
            if not man["segments"] or man["segments"][-1]["count"]>=cfg["segment_events"]:
                seq=man["next_segment"];man["next_segment"]+=1
                seg={"id":seq,"file":f"segments/{seq:020d}.jsonl","count":0,"min_ns":event.timestamp_ns,"max_ns":event.timestamp_ns,"levels":[],"loggers":[],"tags":{}}
                man["segments"].append(seg)
            seg=man["segments"][-1]
            # Atomically publish the complete segment payload.
            segment_path = base+"/"+seg["file"]
            previous = self.vfs.read_file(segment_path) if self.vfs.exists(segment_path) else b""
            payload = previous + (_json(event.to_dict())+"\n").encode()
            # Directory entries are limited to 27 bytes; use a short temp name.
            temp_path = base + "/segments/" + f"tmp{seg["id"]:016d}"
            self.vfs.write_file(temp_path, payload)
            self.vfs.rename(temp_path, segment_path)
            seg["count"]+=1;seg["min_ns"]=min(seg["min_ns"],event.timestamp_ns);seg["max_ns"]=max(seg["max_ns"],event.timestamp_ns);seg["checksum"]=hashlib.sha256(payload).hexdigest()
            if event.level not in seg["levels"]:seg["levels"].append(event.level)
            if event.logger not in seg["loggers"]:seg["loggers"].append(event.logger)
            for k,v in event.tags.items():
                vals=seg["tags"].setdefault(k,[])
                if v not in vals:vals.append(v)
            cfg["sequence"]=man["next_sequence"]
            man["event_ids"][event.event_id]=event.to_dict()
            self._write(base+"/manifest.json.tmp",man);self.vfs.rename(base+"/manifest.json.tmp",base+"/manifest.json")
            self._write(base+"/config.json.tmp",cfg);self.vfs.rename(base+"/config.json.tmp",base+"/config.json");return event
    def append_many(self,stream,events):return [self.append(stream,e) for e in events]
    def query(self,stream,start_ns=None,end_ns=None,levels=None,loggers=None,tags=None,where=None,limit=None,reverse=False):
        with self._lock:
            self._config(stream);base=self._dir(stream);man=self._read(base+"/manifest.json")
            levelset={normalize_level(x) for x in levels} if levels else None;loggers=set(loggers or []);tags={k:str(v) for k,v in (tags or {}).items()}
            rows=[]
            for seg in man["segments"]:
                if start_ns is not None and seg["max_ns"]<start_ns:continue
                if end_ns is not None and seg["min_ns"]>end_ns:continue
                if levelset and not levelset.intersection(seg["levels"]):continue
                if loggers and not loggers.intersection(seg["loggers"]):continue
                if any(v not in seg["tags"].get(k,[]) for k,v in tags.items()):continue
                for line in self.vfs.read_file(base+"/"+seg["file"]).splitlines():
                    raw=json.loads(line);ts=raw["timestamp_ns"]
                    if start_ns is not None and ts<start_ns:continue
                    if end_ns is not None and ts>end_ns:continue
                    if levelset and raw["level"] not in levelset:continue
                    if loggers and raw["logger"] not in loggers:continue
                    if any(str(raw.get("tags",{}).get(k))!=v for k,v in tags.items()):continue
                    if not _match(raw,where):continue
                    rows.append(LogEvent.from_dict(raw))
            rows.sort(key=lambda x:(x.timestamp_ns,x.event_id),reverse=reverse)
            return rows[:limit] if limit is not None else rows
    def cursor(self, stream, consumer="default"):
        self._config(stream); man=self._read(self._dir(stream)+"/manifest.json")
        return int(man.setdefault("consumers",{}).get(consumer,0))
    def ack(self, stream, consumer="default", sequence=None):
        with self._lock:
            self._config(stream); base=self._dir(stream); man=self._read(base+"/manifest.json"); cur=int(man.setdefault("consumers",{}).get(consumer,0)); target=cur if sequence is None else int(sequence)
            # The cursor is the next sequence to deliver; acknowledging sequence N
            # advances replay past N while remaining monotonic/idempotent.
            if target < -1: raise LogDiskError("sequence 不能为负数")
            man["consumers"][consumer]=max(cur,target + 1)
            self._write(base+"/manifest.json.tmp",man); self.vfs.rename(base+"/manifest.json.tmp",base+"/manifest.json")
            return man["consumers"][consumer]
    def replay(self, stream, consumer="default", limit=None, **filters):
        start=self.cursor(stream,consumer); rows=[e for e in self.query(stream,**filters) if (e.sequence or 0)>=start]
        return rows[:limit] if limit is not None else rows
    def count(self, stream, **filters):
        return len(self.query(stream, **filters))
    def tail(self,stream,n=100,**filters):return self.query(stream,reverse=True,limit=n,**filters)[::-1]
    def follow(self,stream,after_ns=None,poll_interval=0.5,stop_event=None,**filters)->Iterator[LogEvent]:
        cursor=after_ns or 0;seen=set()
        while stop_event is None or not stop_event.is_set():
            for event in self.query(stream,start_ns=cursor,**filters):
                if event.event_id in seen:continue
                seen.add(event.event_id);cursor=max(cursor,event.timestamp_ns);yield event
            time.sleep(poll_interval)
    def enforce_retention(self,stream,now_ns=None):
        with self._lock:
            cfg=self._config(stream);base=self._dir(stream);man=self._read(base+"/manifest.json");now_ns=now_ns or time.time_ns();remove=[]
            if cfg.get("retention_seconds") is not None:
                cutoff=now_ns-int(cfg["retention_seconds"]*1_000_000_000);remove.extend(s for s in man["segments"] if s["max_ns"]<cutoff)
            keep=[s for s in man["segments"] if s not in remove]
            max_events=cfg.get("max_events")
            while max_events is not None and sum(s["count"] for s in keep)>max_events and len(keep)>1:remove.append(keep.pop(0))
            for s in remove:
                p=base+"/"+s["file"]
                if self.vfs.exists(p):self.vfs.remove(p)
            man["segments"]=keep;self._write(base+"/manifest.json",man);return sum(s["count"] for s in remove)
    def compact(self,stream):
        with self._lock:
            cfg=self._config(stream);events=self.query(stream);base=self._dir(stream);man=self._read(base+"/manifest.json")
            for s in man["segments"]:
                p=base+"/"+s["file"]
                if self.vfs.exists(p):self.vfs.remove(p)
            self._write(base+"/manifest.json",{"next_segment":0,"next_sequence":man.get("next_sequence",0),"segments":[]})
            for event in events:self.append(stream,event)
            return len(events)
    def stats(self,stream):
        self._config(stream);m=self._read(self._dir(stream)+"/manifest.json")
        return {"stream":stream,"segments":len(m["segments"]),"events":sum(s["count"] for s in m["segments"]),
                "min_ns":min((s["min_ns"] for s in m["segments"]),default=None),"max_ns":max((s["max_ns"] for s in m["segments"]),default=None)}
