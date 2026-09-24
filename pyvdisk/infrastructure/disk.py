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
from .wal import WriteAheadLog, decode_records

class DataDiskError(RuntimeError):
    """Raised for invalid or unmounted data disks."""
class _Missing: pass
MISSING = _Missing()
def _json(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def _enc(v): return base64.b64encode(_json(v)).decode("ascii")
def _dec(v): return json.loads(base64.b64decode(v).decode())

def _enc_entry(value):
    """JSON-safe encoding for compensation entries (bytes become base64 wrappers)."""
    if isinstance(value, bytes): return {"__bytes__": base64.b64encode(value).decode("ascii")}
    if isinstance(value, dict): return {str(k): _enc_entry(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [_enc_entry(v) for v in value]
    return value

def _dec_entry(value):
    if isinstance(value, dict):
        if len(value) == 1 and "__bytes__" in value: return base64.b64decode(value["__bytes__"])
        return {k: _dec_entry(v) for k, v in value.items()}
    if isinstance(value, list): return [_dec_entry(v) for v in value]
    return value

def _tree_paths(vfs, root):
    """Every path under ``root``, deepest first so removals never precede children."""
    out=[]
    if not vfs.exists(root): return out
    stack=[root]
    while stack:
        cur=stack.pop()
        try: names=vfs.listdir(cur)
        except Exception: continue
        for name in names:
            full=f"{cur.rstrip('/')}/{name}" if cur!="/" else f"/{name}"
            out.append(full)
            if vfs.isdir(full): stack.append(full)
    out.sort(key=lambda p: p.count("/"), reverse=True)
    return out

def _apply_undo(vfs, entry):
    """Compensate one recorded mutation. Must stay idempotent: recovery replays it."""
    kind=entry[0]
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
    elif kind=="restore_tree":
        _, root, snap=entry
        for full in _tree_paths(vfs, root):
            if full.lstrip("/") not in snap:
                try: vfs.remove(full)
                except Exception: pass
        for rel in sorted(snap, key=lambda p: (p.count("/"), p)):
            data=snap[rel]; full="/"+rel.lstrip("/")
            if isinstance(data, dict) and data.get("__dir__"):
                if not vfs.exists(full): vfs.makedirs(full)
            elif data is None:
                if vfs.exists(full): vfs.remove(full)
            else:
                vfs.write_file(full, data)

class TransactionParticipant:
    """Small participant contract: prepare/commit/abort, with saga fallback."""
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None

class MetadataTransaction(AbstractContextManager):
    def __init__(self, owner, txid=None):
        self.owner=owner; self.txid=txid or uuid.uuid4().hex; self.changes={}; self.closed=False
        self._participants=[]; self._intents=[]; self._fs_journal=[]; self._pushed=False
        self._compensated=False; self._intents_persisted=False
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
    def _grouped_intents(self):
        """每个 participant 的 intent，保持 enlist 顺序。"""
        return {p: [op for q, op in self._intents if q is p] for p in self._participants}
    def _persist_intents(self):
        """把 intent 落盘（幂等）。

        ``commit()`` 在 prepare 之前逐条写入；而 abort 可能在任何 prepare 发生前就到来，
        恢复端只有能从日志读回 intent 才能补偿，所以这条路径也要写。
        """
        if self._intents_persisted: return
        for p, ops in self._grouped_intents().items():
            self.owner._append_metadata_wal({"kind":"intent","txid":self.txid,"operation":{"participant":type(p).__name__,"count":len(ops)},"intents":_enc_entry(list(ops))})
        self._intents_persisted=True
    def _dispatch_participant_abort(self):
        """按 enlist 的逆序通知 participant 补偿，容忍单个失败。"""
        for p, ops in reversed(list(self._grouped_intents().items())):
            try: p.abort(self.txid, tuple(ops))
            except Exception: pass
    def _active_tx(self):
        vfs=getattr(self.owner, "vfs", None)
        if vfs is None or not getattr(vfs, "_tx_stack", None): return None
        return vfs._tx_stack[-1]
    def _record_fs(self, kind, *args):
        if self._active_tx() is not self: return
        entry=(kind,)+args
        self._fs_journal.append(entry)
        # Write-ahead: the compensation entry is durable before the mutation is applied,
        # so a crash before commit can still be undone from the log alone.
        self.owner._append_compensation(self.txid, entry)
    def _mark_compensated(self):
        if not self._compensated:
            self._compensated=True
            self.owner._append_metadata_wal({"kind":"compensated","txid":self.txid})
    def _unwind_fs(self):
        vfs=getattr(self.owner, "vfs", None)
        if vfs is None: return
        for entry in reversed(self._fs_journal):
            try: _apply_undo(vfs, entry)
            except Exception:
                # best-effort; recovery replays the durable log and retries
                pass
        self._mark_compensated()
    def _detach(self):
        vfs=getattr(self.owner, "vfs", None)
        if vfs is not None and getattr(vfs, "_tx_stack", None) and vfs._tx_stack and vfs._tx_stack[-1] is self:
            vfs._tx_stack.pop()
        self._pushed=False
    def _maybe_checkpoint(self):
        checkpointer=getattr(self.owner,"_maybe_checkpoint_wal",None)
        if checkpointer is not None:
            try: checkpointer()
            except Exception: pass
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
        grouped=self._grouped_intents()
        try:
            for p,ops in grouped.items():
                self.owner._append_metadata_wal({"kind":"intent","txid":self.txid,"operation":{"participant":type(p).__name__,"count":len(ops)},"intents":_enc_entry(list(ops))})
                p.prepare(self.txid, tuple(ops)); self.owner._append_metadata_wal({"kind":"prepare","txid":self.txid,"operation":{"participant":type(p).__name__}})
            self._intents_persisted=True
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
            self._fs_journal.clear(); self._detach(); self._maybe_checkpoint()
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
            self._fs_journal.clear(); self._detach(); self._maybe_checkpoint()
            self.closed=True
            raise
    def abort(self):
        if not self.closed:
            if not any(r.get("txid")==self.txid and r.get("kind") in ("commit", "abort") for r in self.owner._wal_records()):
                self.owner._append_metadata_wal({"kind":"abort","txid":self.txid})
                self.owner._transaction_state(self.txid, "aborted")
            if self._participants:
                # §8.6：已注册的 participant 在这里就收到 abort(txid, intents)，而不是
                # 只等挂载恢复重放日志——否则进程内 abort 后它的事务性副作用会留下来。
                self._persist_intents()
                self._dispatch_participant_abort()
            self._unwind_fs()
            self._fs_journal.clear(); self._detach(); self._maybe_checkpoint()
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
    # mutating: journal before-state first (write-ahead), then delegate
    def write_file(self, path, data, mode=0o644):
        before=self.vfs.read_file(path) if (self.vfs.exists(path) and self.vfs.isfile(path)) else None
        if before is None: self._record("remove", path)
        else: self._record("write", path, before)
        self.vfs.write_file(path, data, mode)
    def append_file(self, path, data):
        before=self.vfs.read_file(path) if (self.vfs.exists(path) and self.vfs.isfile(path)) else None
        if before is not None: self._record("write", path, before)
        self.vfs.append_file(path, data)
    def remove(self, path):
        existed=self.vfs.exists(path)
        snap=_snapshot_dir(self.vfs, path) if (existed and self.vfs.isdir(path)) else None
        before=self.vfs.read_file(path) if (existed and self.vfs.isfile(path)) else None
        if snap is not None: self._record("restore_many", snap)
        elif before is not None: self._record("write", path, before)
        # if missing, nothing to undo
        self.vfs.remove(path)
    def rmtree(self, path):
        snap=_snapshot_dir(self.vfs, path) if self.vfs.exists(path) else {}
        if snap: self._record("restore_many", snap)
        self.vfs.rmtree(path)
    def rename(self, src, dst):
        src_b=self.vfs.read_file(src) if (self.vfs.exists(src) and self.vfs.isfile(src)) else None
        dst_b=self.vfs.read_file(dst) if (self.vfs.exists(dst) and self.vfs.isfile(dst)) else None
        self._record("rename", src, dst, src_b, dst_b)
        self.vfs.rename(src, dst)
    def mkdir(self, path, mode=0o755):
        existed=self.vfs.exists(path)
        if not existed: self._record("rmdir", path)
        self.vfs.mkdir(path, mode)
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
        for p in reversed(missing): self._record("rmdir", p)
        self.vfs.makedirs(path, mode)


class VectorNamespace(TransactionParticipant):
    """Explicit vector collection adapter (saga participant boundary).

    Mutations snapshot the collection directory into the active transaction so a
    crash before the commit record can be compensated at mount time.
    """
    def __init__(self, disk): self.disk = disk
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None
    def __getattr__(self, name): return getattr(self.disk, name)
    def _journal(self, name):
        vfs=self.disk.vfs; stack=getattr(vfs, "_tx_stack", None)
        if stack: stack[-1]._record_fs("restore_tree", self.disk._dir(name), _snapshot_dir(vfs, self.disk._dir(name)))
    def create_collection(self, name, *a, **k):
        self._journal(name); return self.disk.create_collection(name, *a, **k)
    def drop_collection(self, name, *a, **k):
        self._journal(name); return self.disk.drop_collection(name, *a, **k)
    def upsert(self, name, *a, **k):
        self._journal(name); return self.disk.upsert(name, *a, **k)
    def upsert_many(self, name, *a, **k):
        self._journal(name); return self.disk.upsert_many(name, *a, **k)
    def delete(self, name, *a, **k):
        self._journal(name); return self.disk.delete(name, *a, **k)
    list_collections = lambda self: self.disk.list_collections()
    get = lambda self, *a, **k: self.disk.get(*a, **k)
    count = lambda self, *a, **k: self.disk.count(*a, **k)
    search = lambda self, *a, **k: self.disk.search(*a, **k)

class LogNamespace(TransactionParticipant):
    """Explicit structured-log adapter (saga participant boundary).

    Mutations snapshot the stream directory into the active transaction so a
    crash before the commit record can be compensated at mount time.
    """
    def __init__(self, disk): self.disk = disk
    def prepare(self, txid, intents): return None
    def commit(self, txid, intents): return None
    def abort(self, txid, intents): return None
    def __getattr__(self, name): return getattr(self.disk, name)
    def _journal(self, name):
        vfs=self.disk.vfs; stack=getattr(vfs, "_tx_stack", None)
        if stack: stack[-1]._record_fs("restore_tree", self.disk._dir(name), _snapshot_dir(vfs, self.disk._dir(name)))
    def create_stream(self, name, *a, **k):
        self._journal(name); return self.disk.create_stream(name, *a, **k)
    def drop_stream(self, name, *a, **k):
        self._journal(name); return self.disk.drop_stream(name, *a, **k)
    def append(self, stream, *a, **k):
        self._journal(stream); return self.disk.append(stream, *a, **k)
    def append_many(self, stream, *a, **k):
        self._journal(stream); return self.disk.append_many(stream, *a, **k)
    def ack(self, stream, *a, **k):
        self._journal(stream); return self.disk.ack(stream, *a, **k)
    list_streams = lambda self: self.disk.list_streams()
    query = lambda self, *a, **k: self.disk.query(*a, **k)
    count = lambda self, *a, **k: self.disk.count(*a, **k)
    tail = lambda self, *a, **k: self.disk.tail(*a, **k)
    follow = lambda self, *a, **k: self.disk.follow(*a, **k)
    stats = lambda self, *a, **k: self.disk.stats(*a, **k)

def _attach(cls,vfs,lock):
    obj=cls.__new__(cls); obj.path=vfs.path; obj.vfs=vfs; obj._mounted=True; obj._lock=lock; return obj

class DataDisk:
    """One image containing VFS, vectors, logs, checkpoints, WAL and metadata."""
    MANIFEST="/.system/manifest.json"; METADATA="/.system/metadata.json"; WAL="/.system/wal.jsonl"; CHECKPOINT="/.system/checkpoint.json"; TRANSACTIONS="/.system/transactions.json"; WAL_CHECKPOINT="/.system/wal.ckpt.json"; FORMAT="pyvdisk-data"
    WAL_CHECKPOINT_BYTES=256*1024
    def __init__(self,path,block_size=4096, *, legacy=False):
        if legacy:
            warnings.warn(
                "legacy unified aliases are deprecated; prefer DataDisk and its explicit namespaces.",
                DeprecationWarning, stacklevel=2,
            )
        self.path=os.fspath(path); self.block_size=block_size; self.vfs=VFS(self.path,block_size); self._lock=threading.RLock(); self._mounted=False; self._metadata={}
        self._recovery_participants={}; self._recovery_report=None
        self._checkpointing=False; self._wal_checkpoint=None
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
        wal=getattr(self,"wal",None)
        if wal is not None:
            wal.append_record(record); return
        body=dict(record); body["checksum"]=hashlib.sha256(_json(record)).hexdigest()
        data=_json(body)+b"\n"
        self.vfs.append_file(self.WAL,data) if self.vfs.exists(self.WAL) else self.vfs.write_file(self.WAL,data); self._sync()
    def _append_compensation(self,txid,entry):
        """Durably record how to undo one participant mutation (write-ahead undo log)."""
        self._append_metadata_wal({"kind":"undo","txid":txid,"entry":_enc_entry(list(entry))})
    def register_recovery_participant(self,name,factory):
        """Register how to rebuild a participant so mount recovery can compensate it.

        ``factory`` is called with the disk and must return an object exposing
        ``abort(txid, intents)`` (or None when the participant is unavailable).
        """
        self._recovery_participants[name]=factory
        return self
    def _resolve_recovery_participant(self,name):
        factory=self._recovery_participants.get(name)
        if factory is not None:
            try: return factory(self) if callable(factory) else factory
            except Exception: return None
        builtin={"FileNamespace":"fs","VectorNamespace":"vector","LogNamespace":"log"}
        return getattr(self,builtin[name],None) if name in builtin else None
    def _wal_records(self):
        """Every readable record in the log, decoded by the shared WAL reader."""
        wal=getattr(self,"wal",None)
        if wal is not None: return list(wal.records())
        if not self.vfs.exists(self.WAL): return []
        return list(decode_records(self.vfs.read_file(self.WAL)))
    def _transaction_state(self, txid, status):
        states=self._read_json(self.TRANSACTIONS,{})
        states.setdefault(txid,{})["status"]=status
        self._atomic_json(self.TRANSACTIONS,states); self._sync()
    def _recover_transactions(self):
        """Replay the WAL: roll metadata forward/back, then compensate unfinished work.

        Metadata is redone when the transaction durably committed and rolled back
        otherwise. Every transaction without a ``commit`` record additionally has its
        durable write-ahead undo entries replayed in reverse, so participant side
        effects (filesystem, vector and log namespaces) cannot survive a crash that
        happened after the participant acted but before the commit record.
        """
        order,ops,done,aborted={}, {}, set(), set()
        undo,intents,compensated={}, {}, set()
        for item in self._wal_records():
            kind=item.get("kind"); tid=item.get("txid")
            if tid is not None and tid not in order: order[tid]=len(order)
            try:
                if kind=="begin":ops.setdefault(tid,[])
                elif kind=="operation":ops.setdefault(tid,[]).append(item["operation"])
                elif kind=="undo":undo.setdefault(tid,[]).append(_dec_entry(item.get("entry")))
                elif kind=="intent":
                    payload=_dec_entry(item.get("intents") or [])
                    intents.setdefault(tid,[]).append(((item.get("operation") or {}).get("participant"),payload))
                elif kind=="commit":done.add(tid)
                elif kind=="abort":aborted.add(tid)
                elif kind=="compensated":compensated.add(tid)
            except (ValueError,KeyError,TypeError):break
        state=self._read_json(self.METADATA,{})
        for tid,entries in ops.items():
            if tid in aborted: continue
            for op in (entries if tid in done else reversed(entries)):
                committed=tid in done; missing=op["after_missing"] if committed else op["before_missing"]; value=_dec(op["after"] if committed else op["before"])
                if missing:state.pop(op["key"],None)
                else:state[op["key"]]=value
        self._atomic_json(self.METADATA,state); self._metadata=state
        report={"compensated":[],"committed":[],"aborted":[],"participants":[]}
        for tid in sorted(order,key=order.get):
            if tid in done:
                report["committed"].append(tid); continue
            if tid in aborted: report["aborted"].append(tid)
            if tid not in compensated:
                for entry in reversed(undo.get(tid,[])):
                    try: _apply_undo(self.vfs,entry)
                    except Exception: pass
                # Written last so a crash during compensation simply replays it.
                self._append_metadata_wal({"kind":"compensated","txid":tid})
                compensated.add(tid); report["compensated"].append(tid)
            for name,payload in intents.get(tid,()):
                participant=self._resolve_recovery_participant(name)
                if participant is None: continue
                try:
                    participant.abort(tid,tuple(payload))
                    report["participants"].append({"txid":tid,"participant":name})
                except Exception: pass
        self._recovery_report=report
        return report
    def recovery_report(self):
        """Result of the last mount-time recovery (None before the first mount)."""
        return self._recovery_report
    def checkpoint_wal(self):
        """Settle every recorded transaction and truncate the log.

        A checkpoint is only legal with no open transaction. At that point every
        transaction in the log is either committed -- its effects are already
        published to METADATA and to the namespaces -- or unfinished, and unfinished
        work is compensated before its log records may be dropped. Committed work
        therefore needs no redo after a checkpoint, and recovery no longer replays
        the whole history on every mount.
        """
        with self._lock:
            if not self._mounted: raise DataDiskError("data disk not mounted")
            if self._checkpointing: return self._wal_checkpoint
            if getattr(self.vfs,"_tx_stack",None): return self._wal_checkpoint
            self._checkpointing=True
            try:
                records=len(self._wal_records())
                if not records: return self._wal_checkpoint
                self._recover_transactions()
                self.wal.truncate()
                info={"truncated_records":records,"truncated_at_ns":time.time_ns(),"remaining_bytes":self.wal.size(),"truncated":self._recovery_report}
                self._atomic_json(self.WAL_CHECKPOINT,info); self._sync()
                self._wal_checkpoint=info
                return info
            finally:
                self._checkpointing=False
    def _maybe_checkpoint_wal(self,force=False):
        """Truncate once the log is large enough, or unconditionally on shutdown."""
        if not self._mounted or self._checkpointing: return None
        if getattr(self.vfs,"_tx_stack",None): return None
        if not force and self.wal.size()<self.WAL_CHECKPOINT_BYTES: return None
        try: return self.checkpoint_wal()
        except Exception: return None
    def wal_stats(self):
        """Current log occupancy plus the last truncation boundary, if any."""
        wal=getattr(self,"wal",None)
        return {"bytes":wal.size() if wal is not None else 0,"records":len(self._wal_records()),"checkpoint":self._wal_checkpoint}
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
                self._wal_checkpoint=self._read_json(self.WAL_CHECKPOINT,self._wal_checkpoint)
                if self.vfs.exists(self.WAL) and self._wal_records():self._recover_transactions()
                elif self._recovery_report is None:self._recovery_report={"compensated":[],"committed":[],"aborted":[],"participants":[]}
                self._mounted=True; return self
            except Exception:self.vfs.close(); raise
    open=mount
    def close(self):
        with self._lock:
            if self._mounted:
                self._maybe_checkpoint_wal(force=True)
                self._sync(); self.vfs.close(); self._mounted=False; self.vector._mounted=self.log._mounted=False
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