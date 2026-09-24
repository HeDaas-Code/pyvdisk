"""Shared write-ahead log for DataDisk and VScript transactions.

One record codec, one record-kind vocabulary and one recovery algorithm serve both
the container log (VFS-backed, ``DataDisk.wal``) and a VScript transaction log
(host-file backed). Only the byte backend differs, which is what used to make the
two implementations drift apart: the readers disagreed about which kinds exist, so
one of them silently truncated the log at the first record it did not recognise.
"""
from __future__ import annotations
import hashlib, json, os, uuid
from pathlib import Path

# Every kind either writer may put in the log. A reader must never stop at a kind it
# does not know: stopping would hide every later commit record and turn a committed
# transaction back into a pending one.
RECORD_KINDS = {"begin","intent","prepare","apply","operation","commit","abort","undo","compensated"}
DEFAULT_PATH = "/.system/wal.jsonl"

def canonical_json(value) -> bytes:
    """The exact byte view a checksum is computed over."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def encode_record(record) -> bytes:
    body=dict(record)
    body["checksum"]=hashlib.sha256(canonical_json(body)).hexdigest()
    return (json.dumps(body, sort_keys=True, ensure_ascii=False) + "\n").encode()

def decode_records(data: bytes):
    """Decode a log prefix; a corrupt or unknown record ends the readable prefix."""
    out=[]
    for line in data.splitlines():
        if not line.strip(): continue
        try:
            item=json.loads(line)
            checksum=item.pop("checksum")
            if hashlib.sha256(canonical_json(item)).hexdigest()!=checksum: break
            if item.get("kind") not in RECORD_KINDS: break
        except (ValueError,KeyError,TypeError): break
        out.append(item)
    return out

class VFSBackend:
    """Log bytes living inside a VDisk image."""
    def __init__(self, vfs, path=DEFAULT_PATH): self.vfs=vfs; self.path=path
    def exists(self): return self.vfs.exists(self.path)
    def read(self): return self.vfs.read_file(self.path) if self.vfs.exists(self.path) else b""
    def size(self):
        try: return len(self.read())
        except Exception: return 0
    def append(self, data):
        if self.vfs.exists(self.path): self.vfs.append_file(self.path, data)
        else: self.vfs.write_file(self.path, data)
        self.sync()
    def sync(self):
        try:
            self.vfs.disk.flush()
            handle=getattr(self.vfs.disk, "_f", None)
            if handle is not None: os.fsync(handle.fileno())
        except Exception: pass
    def reset(self):
        if self.vfs.exists(self.path): self.vfs.remove(self.path)

class FileBackend:
    """Log bytes living on the host filesystem (VScript transaction logs)."""
    def __init__(self, path):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
    def exists(self): return self.path.exists()
    def read(self): return self.path.read_bytes() if self.path.exists() else b""
    def size(self):
        try: return self.path.stat().st_size
        except OSError: return 0
    def append(self, data):
        with self.path.open("ab") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
    def sync(self): pass
    def reset(self):
        try: self.path.unlink()
        except FileNotFoundError: pass

class WriteAheadLog:
    """Append-only, checksummed JSONL transaction log.

    ``WriteAheadLog(vfs)`` logs inside an image; ``WriteAheadLog("/tmp/tx.wal")``
    logs on the host. Both share this codec, the kind vocabulary and ``recover``.
    """
    def __init__(self, target, path=None):
        if isinstance(target, (VFSBackend, FileBackend)): self.backend=target
        elif isinstance(target, (str, os.PathLike)): self.backend=FileBackend(target)
        elif hasattr(target, "read_file") and hasattr(target, "write_file"): self.backend=VFSBackend(target, path or DEFAULT_PATH)
        else: raise TypeError("WriteAheadLog needs a VFS, a filesystem path or a backend")
        self._sequence=self._last_sequence(); self._size=None
    @property
    def path(self): return self.backend.path
    # ---- writers -------------------------------------------------------------
    def append_record(self, record, sequence=False):
        """Append an already-shaped record (used by DataDisk's transaction protocol)."""
        body=dict(record)
        if sequence:
            self._sequence+=1; body["sequence"]=self._sequence
        data=encode_record(body)
        self.backend.append(data)
        if self._size is None: self._size=self.backend.size()
        else: self._size+=len(data)
        return body
    def _append(self, kind, txid, operation=None):
        return self.append_record({"kind":kind,"txid":txid,"operation":operation}, sequence=True)["txid"]
    def begin(self, txid=None): return self._append("begin", txid or uuid.uuid4().hex)
    def append(self, txid, operation):
        if not isinstance(operation, dict): raise TypeError("WAL operation must be a dict")
        return self._append("operation", txid, operation)
    def intent(self, txid, operation=None): return self._append("intent", txid, operation)
    def prepare(self, txid, operation=None): return self._append("prepare", txid, operation)
    def apply(self, txid): return self._append("apply", txid)
    def commit(self, txid): return self._append("commit", txid)
    def abort(self, txid): return self._append("abort", txid)
    # ---- readers -------------------------------------------------------------
    def _read(self): return decode_records(self.backend.read())
    def records(self): return tuple(self._read())
    def _last_sequence(self): return max((int(r.get("sequence") or 0) for r in self._read()), default=0)
    def recover(self, undo=None, redo=None):
        """Return ``(committed, pending)``; callbacks get operations (redo order / undo reverse)."""
        tx={}; committed=set(); aborted=set()
        for r in self._read():
            kind=r.get("kind")
            if kind=="begin": tx.setdefault(r["txid"],[])
            elif kind=="operation": tx.setdefault(r["txid"],[]).append(r["operation"])
            elif kind=="commit": committed.add(r["txid"])
            elif kind=="abort": aborted.add(r["txid"])
        done=[];pending=[]
        for tid,ops in tx.items():
            if tid in aborted: continue
            (done if tid in committed else pending).append((tid,tuple(ops)))
        if redo:
            for _,ops in done:
                for op in ops: redo(op)
        if undo:
            for _,ops in pending:
                for op in reversed(ops): undo(op)
        return tuple(done),tuple(pending)
    # ---- maintenance ---------------------------------------------------------
    def size(self):
        if self._size is None: self._size=self.backend.size()
        return self._size
    def truncate(self):
        """Drop every record. Only legal once all recorded work is settled."""
        self.backend.reset(); self._sequence=0; self._size=0

WAL=WriteAheadLog
