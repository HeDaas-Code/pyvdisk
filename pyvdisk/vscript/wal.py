"""Small, honest write-ahead log for VScript transactions."""
from __future__ import annotations
import hashlib, json, os, uuid
from pathlib import Path

class WriteAheadLog:
    """Append-only JSONL WAL; fsyncs each record, but no locking or atomic data-store commit."""
    def __init__(self, path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self._sequence = self._last_sequence()
    @staticmethod
    def _body(kind, txid, operation, sequence):
        return {"kind": kind, "txid": txid, "operation": operation, "sequence": sequence}
    @classmethod
    def _line(cls, kind, txid, operation, sequence):
        body=cls._body(kind,txid,operation,sequence)
        raw=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
        body["checksum"]=hashlib.sha256(raw).hexdigest()
        return (json.dumps(body, sort_keys=True, ensure_ascii=False) + "\n").encode()
    def _read(self):
        out=[]
        if not self.path.exists(): return out
        with self.path.open("rb") as f:
            for line in f:
                try:
                    item=json.loads(line); checksum=item.pop("checksum")
                    raw=json.dumps(item,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
                    if hashlib.sha256(raw).hexdigest()!=checksum: break
                    if item["kind"] not in {"begin","operation","commit"}: break
                    out.append(item)
                except (ValueError,KeyError,TypeError): break
        return out
    def _last_sequence(self):
        records=self._read(); return records[-1]["sequence"] if records else 0
    def _append(self,kind,txid,operation=None):
        self._sequence+=1
        with self.path.open("ab") as f:
            f.write(self._line(kind,txid,operation,self._sequence)); f.flush(); os.fsync(f.fileno())
        return txid
    def begin(self,txid=None): return self._append("begin",txid or uuid.uuid4().hex)
    def append(self,txid,operation):
        if not isinstance(operation,dict): raise TypeError("WAL operation must be a dict")
        return self._append("operation",txid,operation)
    def commit(self,txid): return self._append("commit",txid)
    def records(self): return tuple(self._read())
    def recover(self, undo=None, redo=None):
        """Return (committed, pending); callbacks receive operations (redo order / undo reverse)."""
        tx={}; committed=set()
        for r in self._read():
            if r["kind"]=="begin": tx.setdefault(r["txid"],[])
            elif r["kind"]=="operation": tx.setdefault(r["txid"],[]).append(r["operation"])
            elif r["kind"]=="commit": committed.add(r["txid"])
        done=[]; pending=[]
        for tid,ops in tx.items(): (done if tid in committed else pending).append((tid,tuple(ops)))
        if redo:
            for _,ops in done:
                for op in ops: redo(op)
        if undo:
            for _,ops in pending:
                for op in reversed(ops): undo(op)
        return tuple(done),tuple(pending)
WAL=WriteAheadLog