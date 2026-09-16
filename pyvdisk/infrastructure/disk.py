"""Canonical unified on-disk data infrastructure."""
from __future__ import annotations
import base64, hashlib, json, os, threading, time, uuid
import warnings
from contextlib import AbstractContextManager
from typing import Any
from ..vfs import VFS
from ..vector_disk import VectorDisk
from ..log_disk import LogDisk
from .checkpoint import CheckpointStore
from .wal import WriteAheadLog

class DataDiskError(RuntimeError):
    """Raised for invalid or unmounted data disks."""
class _Missing: pass
MISSING = _Missing()
def _json(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def _enc(v): return base64.b64encode(_json(v)).decode("ascii")
def _dec(v): return json.loads(base64.b64decode(v).decode())

class TransactionParticipant:
    """Small participant contract: prepare/commit/abort, with saga fallback."""
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None

class MetadataTransaction(AbstractContextManager):
    def __init__(self, owner, txid=None):
        self.owner=owner; self.txid=txid or uuid.uuid4().hex; self.changes={}; self.closed=False
        self._participants=[]; self._intents=[]; self._fs_journal=[]; self._pushed=False
    def set(self,key,value):
        if not isinstance(key,str) or not key: raise TypeError("metadata key must be a non-empty string")
        self.changes[key]=value; return self
    def delete(self,key): return self.set(key,MISSING)
    def enlist(self, participant, intent=None):
        if not all(callable(getattr(participant, n, None)) for n in ("prepare","commit","abort")):
            raise TypeError("participant must implement prepare, commit and abort")
        if participant not in self._participants:
            self._participants.append(participant)
        if intent is not None: self.intent(participant, intent)
        return self
    def intent(self, participant, operation):
        if participant not in self._participants: self.enlist(participant)
        if not isinstance(operation, dict): raise TypeError("operation intent must be a dict")
        self._intents.append((participant, dict(operation))); return self
    def _active_tx(self):
        vfs=getattr(self.owner, "vfs", None)
        if vfs is None or not getattr(vfs, "_tx_stack", None): return None
        return vfs._tx_stack[-1]
    def _record_fs(self, kind, *args):
        if self._active_tx() is self:
            self._fs_journal.append((kind,) + args)
    def _unwind_fs(self):
        vfs=getattr(self.owner, "vfs", None)
        if vfs is None: return
        for entry in reversed(self._fs_journal):
            kind=entry[0]
            try:
                if kind=="write":
                    _, path, before=entry
                    if before is None:
                        if vfs.exists(path): vfs.remove(path)
                    else:
                        vfs.write_file(path, before)
                elif kind=="remove":
                    _, path=entry
                    if vfs.exists(path): vfs.remove(path)
                elif kind=="rmdir":
                    _, path=entry
                    if vfs.exists(path) and vfs.isdir(path): vfs.rmdir(path)
                elif kind=="mkdirs":
                    _, path=entry
                    if vfs.exists(path) and vfs.isdir(path): vfs.rmdir(path)
                elif kind=="rename":
                    _, src, dst, src_b, dst_b=entry
                    if vfs.exists(dst): vfs.remove(dst)
                    if src_b is None:
                        if vfs.exists(src): vfs.remove(src)
                    else:
                        vfs.write_file(src, src_b)
                    if dst_b is not None:
                        vfs.write_file(dst, dst_b)
                elif kind=="restore_many":
                    _, snap=entry
                    for rel, data in snap.items():
                        full="/"+rel.lstrip("/")
                        if isinstance(data, dict) and data.get("__dir__"):
                            if not vfs.exists(full): vfs.mkdir(full)
                        elif data is None:
                            if vfs.exists(full): vfs.remove(full)
                        else:
                            vfs.write_file(full, data)
            except Exception:
                # best-effort; partial unwind is acceptable for crash recovery
                pass
    def _detach(self):
        vfs=getattr(self.owner, "vfs", None)
        if vfs is not None and getattr(vfs, "_tx_stack", None) and vfs._tx_stack and vfs._tx_stack[-1] is self:
            vfs._tx_stack.pop()
        self._pushed=False
    def __enter__(self):
        self.owner._append_metadata_wal({"kind":"begin","txid":self.txid})
        vfs=getattr(self.owner, "vfs", None)
        if vfs is not None and hasattr(vfs, "_tx_stack"):
            vfs._tx_stack.append(self); self._pushed=True
        return self
    def commit(self):
        if self.closed:return self
        records=self.owner._wal_records() if hasattr(self.owner, "_wal_records") else []
        if any(r.get("txid")==self.txid and r.get("kind") in ("commit", "abort") for r in records):
            self.closed=True; self._fs_journal.clear(); self._detach(); return self
        old=dict(self.owner._metadata)
        for key,after in self.changes.items():
            before=old.get(key,MISSING)
            op={"key":key,"before":_enc(None if before is MISSING else before),"before_missing":before is MISSING,"after":_enc(None if after is MISSING else after),"after_missing":after is MISSING}
            self.owner._append_metadata_wal({"kind":"operation","txid":self.txid,"operation":op})
        grouped={p: [op for q,op in self._intents if q is p] for p in self._participants}
        try:
            for p,ops in grouped.items():
                self.owner._append_metadata_wal({"kind":"intent","txid":self.txid,"operation":{"participant":type(p).__name__,"count":len(ops)}})
                p.prepare(self.txid, tuple(ops)); self.owner._append_metadata_wal({"kind":"prepare","txid":self.txid,"operation":{"participant":type(p).__name__}})
            new=dict(old)
            for key,value in self.changes.items():
                if value is MISSING:new.pop(key,None)
                else:new[key]=value
            self.owner._append_metadata_wal({"kind":"apply","txid":self.txid})
            self.owner._atomic_json(self.owner.METADATA,new); self.owner._metadata=new
            for p,ops in grouped.items(): p.commit(self.txid, tuple(ops))
            self.owner._append_metadata_wal({"kind":"commit","txid":self.txid})
            self.owner._transaction_state(self.txid, "committed")
            self.owner._atomic_json(self.owner.CHECKPOINT,{"last_txid":self.txid,"time_ns":time.time_ns(),"status":"committed"})
            self._fs_journal.clear(); self._detach()
            self.closed=True; return self
        except Exception:
            self.owner._atomic_json(self.owner.METADATA, old)
            self.owner._metadata = old
            for p,ops in reversed(list(grouped.items())):
                try: p.abort(self.txid, tuple(ops))
                except Exception: pass
            self.owner._append_metadata_wal({"kind":"abort","txid":self.txid})
            self.owner._transaction_state(self.txid, "aborted")
            self._unwind_fs()
            self._fs_journal.clear(); self._detach()
            self.closed=True
            raise
    def abort(self):
        if not self.closed:
            if not any(r.get("txid")==self.txid and r.get("kind") in ("commit", "abort") for r in self.owner._wal_records()):
                self.owner._append_metadata_wal({"kind":"abort","txid":self.txid})
                self.owner._transaction_state(self.txid, "aborted")
            self._unwind_fs()
            self._fs_journal.clear(); self._detach()
            self.closed=True
        return self
    def __exit__(self,exc_type,exc,tb):
        if exc_type is None:self.commit()
        else:self.abort()
        return False

def _snapshot_dir(vfs, path):
    snap={}
    if not vfs.exists(path): return snap
    if path and path != "/":
        snap[path.lstrip("/")] = {"__dir__": True}
    stack=[path]
    while stack:
        cur=stack.pop()
        try: entries=vfs.listdir(cur)
        except Exception: continue
        for name in entries:
            full=f"{cur.rstrip('/')}/{name}" if cur!="/" else f"/{name}"
            if vfs.isdir(full):
                snap[full.lstrip("/")] = {"__dir__": True}
                stack.append(full)
            else:
                try: snap[full.lstrip("/")]=vfs.read_file(full)
                except Exception: snap[full.lstrip("/")]=None
    return snap

class FileNamespace(TransactionParticipant):
    """File-system adapter with transactional undo journal.

    When a MetadataTransaction is active on the VFS, mutating methods record
    before-state on the transaction's journal so abort() can compensate.
    Outside a transaction the adapter is a thin pass-through to the VFS.
    """
    def __init__(self, vfs): self.vfs = vfs
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None
    def __getattr__(self, name): return getattr(self.vfs, name)
    def _tx(self):
        stack=getattr(self.vfs, "_tx_stack", None)
        return stack[-1] if stack else None
    def _record(self, kind, *args):
        tx=self._tx()
        if tx is not None: tx._record_fs(kind, *args)
    # read-only pass-throughs
    def exists(self, path): return self.vfs.exists(path)
    def isfile(self, path): return self.vfs.isfile(path)
    def isdir(self, path): return self.vfs.isdir(path)
    def listdir(self, path="/"): return self.vfs.listdir(path)
    def read_file(self, path): return self.vfs.read_file(path)
    def stat(self, path, follow=True): return self.vfs.stat(path, follow)
    def open(self, path, mode="rb"): return self.vfs.open(path, mode)
    def walk(self, top="/"): return self.vfs.walk(top)
    def statfs(self): return self.vfs.statfs()
    def df(self): return self.vfs.df()
    def du(self, path="/"): return self.vfs.du(path)
    def fsck(self, repair=False): return self.vfs.fsck(repair)
    # mutating: journal before-state, then delegate
    def write_file(self, path, data, mode=0o644):
        before=None
        if self.vfs.exists(path) and self.vfs.isfile(path):
            before=self.vfs.read_file(path)
        self.vfs.write_file(path, data, mode)
        if before is None: self._record("remove", path)
        else: self._record("write", path, before)
    def append_file(self, path, data):
        before=None
        if self.vfs.exists(path) and self.vfs.isfile(path):
            before=self.vfs.read_file(path)
        self.vfs.append_file(path, data)
        if before is not None: self._record("write", path, before)
    def remove(self, path):
        snap=None
        if self.vfs.exists(path) and self.vfs.isdir(path):
            snap=_snapshot_dir(self.vfs, path)
        before=None
        if self.vfs.exists(path) and self.vfs.isfile(path):
            before=self.vfs.read_file(path)
        self.vfs.remove(path)
        if snap is not None: self._record("restore_many", snap)
        elif before is not None: self._record("write", path, before)
        # if missing, nothing to undo
    def rmtree(self, path):
        snap=_snapshot_dir(self.vfs, path) if self.vfs.exists(path) else {}
        self.vfs.rmtree(path)
        if snap: self._record("restore_many", snap)
    def rename(self, src, dst):
        src_b=self.vfs.read_file(src) if (self.vfs.exists(src) and self.vfs.isfile(src)) else None
        dst_b=self.vfs.read_file(dst) if (self.vfs.exists(dst) and self.vfs.isfile(dst)) else None
        self.vfs.rename(src, dst)
        self._record("rename", src, dst, src_b, dst_b)
    def mkdir(self, path, mode=0o755):
        existed=self.vfs.exists(path)
        self.vfs.mkdir(path, mode)
        if not existed: self._record("rmdir", path)
    def makedirs(self, path, mode=0o755):
        # Record each missing ancestor shallow→deep so undo removes deepest first
        missing=[]
        cur=path
        while cur and cur not in ("/", ""):
            if self.vfs.exists(cur) and self.vfs.isdir(cur): break
            missing.append(cur)
            parent=cur.rsplit("/", 1)[0] if "/" in cur else "/"
            if parent==cur: break
            cur=parent
        # missing is deepest→shallowest; record shallow→deep so reverse undo
        # removes deepest first.
        self.vfs.makedirs(path, mode)
        for p in reversed(missing): self._record("rmdir", p)


class VectorNamespace(TransactionParticipant):
    """Explicit vector collection adapter (saga participant boundary)."""
    def __init__(self, disk): self.disk = disk
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None
    def __getattr__(self, name): return getattr(self.disk, name)
    create_collection = lambda self, *a, **k: self.disk.create_collection(*a, **k)
    list_collections = lambda self: self.disk.list_collections()
    drop_collection = lambda self, *a, **k: self.disk.drop_collection(*a, **k)
    upsert = lambda self, *a, **k: self.disk.upsert(*a, **k)
    upsert_many = lambda self, *a, **k: self.disk.upsert_many(*a, **k)
    get = lambda self, *a, **k: self.disk.get(*a, **k)
    delete = lambda self, *a, **k: self.disk.delete(*a, **k)
    count = lambda self, *a, **k: self.disk.count(*a, **k)
    search = lambda self, *a, **k: self.disk.search(*a, **k)

class LogNamespace(TransactionParticipant):
    """Explicit structured-log adapter (saga participant boundary)."""
    def __init__(self, disk): self.disk = disk
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None
    def __getattr__(self, name): return getattr(self.disk, name)
    create_stream = lambda self, *a, **k: self.disk.create_stream(*a, **k)
    list_streams = lambda self: self.disk.list_streams()
    drop_stream = lambda self, *a, **k: self.disk.drop_stream(*a, **k)
    append = lambda self, *a, **k: self.disk.append(*a, **k)
    append_many = lambda self, *a, **k: self.disk.append_many(*a, **k)
    query = lambda self, *a, **k: self.disk.query(*a, **k)
    count = lambda self, *a, **k: self.disk.count(*a, **k)
    tail = lambda self, *a, **k: self.disk.tail(*a, **k)
    follow = lambda self, *a, **k: self.disk.follow(*a, **k)
    stats = lambda self, *a, **k: self.disk.stats(*a, **k)

def _attach(cls,vfs,lock):
    obj=cls.__new__(cls); obj.path=vfs.path; obj.vfs=vfs; obj._mounted=True; obj._lock=lock; return obj

class DataDisk:
    """One image containing VFS, vectors, logs, checkpoints, WAL and metadata."""
    MANIFEST="/.system/manifest.json"; METADATA="/.system/metadata.json"; WAL="/.system/wal.jsonl"; CHECKPOINT="/.system/checkpoint.json"; TRANSACTIONS="/.system/transactions.json"; FORMAT="pyvdisk-data"
    def __init__(self,path,block_size=4096, *, legacy=False):
        if legacy:
            warnings.warn(
                "legacy unified aliases are deprecated; prefer DataDisk and its explicit namespaces.",
                DeprecationWarning, stacklevel=2,
            )
        self.path=os.fspath(path); self.block_size=block_size; self.vfs=VFS(self.path,block_size); self._lock=threading.RLock(); self._mounted=False; self._metadata={}
    @classmethod
    def create(cls,path,size_bytes,block_size=4096,label=""):
        VFS.create(os.fspath(path),size_bytes,block_size,label=label)
        with VFS(os.fspath(path),block_size) as v:
            v.makedirs("/.system"); v.mkdir("/.vectors"); v.mkdir("/.logs")
            v.write_file("/.vector_disk.json",b'{"type":"vector","version":1}'); v.write_file("/.log_disk.json",b'{"type":"log","version":1}')
            v.write_file(cls.MANIFEST,_json({"type":cls.FORMAT,"version":1,"block_size":block_size,"namespaces":["fs","vectors","logs","checkpoints","wal"]}))
            v.write_file(cls.METADATA,b"{}"); v.write_file(cls.CHECKPOINT,b'{"last_txid":null}'); v.write_file(cls.TRANSACTIONS,b"{}")
        return cls(path,block_size)
    def _read_json(self,path,default):
        if not self.vfs.exists(path):return default
        return json.loads(self.vfs.read_file(path).decode())
    def _atomic_json(self,path,value):
        tmp=path+".t"+uuid.uuid4().hex[:8]; self.vfs.write_file(tmp,_json(value)); self.vfs.rename(tmp,path)
    def _sync(self):
        self.vfs.disk.flush(); h=getattr(self.vfs.disk,"_f",None)
        if h is not None: os.fsync(h.fileno())
    def _append_metadata_wal(self,record):
        body=dict(record); body["checksum"]=hashlib.sha256(_json(record)).hexdigest()
        data=_json(body)+b"\n"
        self.vfs.append_file(self.WAL,data) if self.vfs.exists(self.WAL) else self.vfs.write_file(self.WAL,data); self._sync()
    def _wal_records(self):
        if not self.vfs.exists(self.WAL): return []
        out=[]
        for line in self.vfs.read_file(self.WAL).splitlines():
            try:
                item=json.loads(line); checksum=item.pop("checksum")
                if hashlib.sha256(_json(item)).hexdigest()!=checksum: break
                out.append(item)
            except (ValueError,KeyError,TypeError): break
        return out
    def _transaction_state(self, txid, status):
        states=self._read_json(self.TRANSACTIONS,{})
        states.setdefault(txid,{})["status"]=status
        self._atomic_json(self.TRANSACTIONS,states); self._sync()
    def _recover_metadata(self):
        tx,done,aborted={},set(),set()
        if self.vfs.exists(self.WAL):
            for line in self.vfs.read_file(self.WAL).splitlines():
                try:
                    item=json.loads(line); checksum=item.pop("checksum")
                    if hashlib.sha256(_json(item)).hexdigest()!=checksum:break
                    if item.get("kind")=="begin":tx.setdefault(item["txid"],[])
                    elif item.get("kind")=="operation":tx.setdefault(item["txid"],[]).append(item["operation"])
                    elif item.get("kind")=="commit":done.add(item["txid"])
                    elif item.get("kind")=="abort":aborted.add(item["txid"])
                except (ValueError,KeyError,TypeError):break
        state=self._read_json(self.METADATA,{})
        for tid,ops in tx.items():
            if tid in aborted: continue
            for op in (ops if tid in done else reversed(ops)):
                committed=tid in done; missing=op["after_missing"] if committed else op["before_missing"]; value=_dec(op["after"] if committed else op["before"])
                if missing:state.pop(op["key"],None)
                else:state[op["key"]]=value
        self._atomic_json(self.METADATA,state); self._metadata=state
    def mount(self):
        with self._lock:
            if self._mounted:return self
            self.vfs.mount()
            try:
                m=self._read_json(self.MANIFEST,None)
                if not isinstance(m,dict) or m.get("type") not in (self.FORMAT,"pyvdisk-unified"):
                    raise DataDiskError("not a PyVDisk data container")
                self._vector_disk=_attach(VectorDisk,self.vfs,self._lock); self._log_disk=_attach(LogDisk,self.vfs,self._lock)
                self.fs=FileNamespace(self.vfs)
                self.vector=self.vectors=VectorNamespace(self._vector_disk); self.vector_disk=self.vector
                self.log=self.logs=LogNamespace(self._log_disk); self.log_disk=self.log
                self.checkpoints=CheckpointStore(self.vfs); self.wal=WriteAheadLog(self.vfs); self._metadata=self._read_json(self.METADATA,{})
                if self.vfs.exists(self.WAL):self._recover_metadata()
                self._mounted=True; return self
            except Exception:self.vfs.close(); raise
    open=mount
    def close(self):
        with self._lock:
            if self._mounted:self._sync(); self.vfs.close(); self._mounted=False; self.vector._mounted=self.log._mounted=False
    def __enter__(self):return self.mount()
    def __exit__(self,*exc):self.close()
    @property
    def mounted(self):return self._mounted
    def manifest(self):
        if not self._mounted:raise DataDiskError("data disk not mounted")
        return self._read_json(self.MANIFEST,{})
    def transaction(self, txid=None):
        if not self._mounted:raise DataDiskError("data disk not mounted")
        return MetadataTransaction(self, txid)
    def get_metadata(self,key,default=None):
        if not self._mounted:raise DataDiskError("data disk not mounted")
        return self._metadata.get(key,default)
    def set_metadata(self,key,value):
        with self.transaction() as tx:tx.set(key,value)
    def scoped(self, context):
        from .capabilities import ScopedDataDisk
        if not self._mounted:
            raise DataDiskError("data disk not mounted")
        return ScopedDataDisk(self, context)

__all__=["DataDisk","DataDiskError","TransactionParticipant","MetadataTransaction","FileNamespace","VectorNamespace","LogNamespace"]