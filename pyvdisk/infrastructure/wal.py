"""A VDisk-backed WAL with the legacy WriteAheadLog interface."""
from __future__ import annotations
import hashlib,json,uuid

class WriteAheadLog:
    def __init__(self,vfs,path="/.system/wal.jsonl"):
        self.vfs=vfs; self.path=path; self._sequence=self._last_sequence()
    @staticmethod
    def _line(kind,txid,operation,sequence):
        body={"kind":kind,"txid":txid,"operation":operation,"sequence":sequence}
        raw=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); body["checksum"]=hashlib.sha256(raw).hexdigest()
        return (json.dumps(body,sort_keys=True,ensure_ascii=False)+"\n").encode()
    def _read(self):
        if not self.vfs.exists(self.path):return []
        out=[]
        for line in self.vfs.read_file(self.path).splitlines():
            try:
                item=json.loads(line); checksum=item.pop("checksum"); raw=json.dumps(item,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
                if hashlib.sha256(raw).hexdigest()!=checksum or item["kind"] not in {"begin","intent","prepare","operation","commit","abort"}:break
                out.append(item)
            except (ValueError,KeyError,TypeError):break
        return out
    def _last_sequence(self):
        r=self._read(); return max((int(item.get("sequence", 0)) for item in r), default=0)
    def _append(self,kind,txid,operation=None):
        self._sequence+=1; data=self._line(kind,txid,operation,self._sequence)
        if self.vfs.exists(self.path):self.vfs.append_file(self.path,data)
        else:self.vfs.write_file(self.path,data)
        return txid
    def begin(self,txid=None):return self._append("begin",txid or uuid.uuid4().hex)
    def append(self,txid,operation):
        if not isinstance(operation,dict):raise TypeError("WAL operation must be a dict")
        return self._append("operation",txid,operation)
    def prepare(self,txid,operation=None):return self._append("prepare",txid,operation)
    def commit(self,txid):return self._append("commit",txid)
    def abort(self,txid):return self._append("abort",txid)
    def records(self):return tuple(self._read())
    def recover(self,undo=None,redo=None):
        tx={}; committed=set(); aborted=set()
        for r in self._read():
            if r["kind"]=="begin":tx.setdefault(r["txid"],[])
            elif r["kind"]=="operation":tx.setdefault(r["txid"],[]).append(r["operation"])
            elif r["kind"] == "commit":committed.add(r["txid"])
            elif r["kind"] == "abort":aborted.add(r["txid"])
        done=[];pending=[]
        for tid,ops in tx.items():
            if tid in aborted: continue
            (done if tid in committed else pending).append((tid,tuple(ops)))
        if redo:
            for _,ops in done:
                for op in ops:redo(op)
        if undo:
            for _,ops in pending:
                for op in reversed(ops):undo(op)
        return tuple(done),tuple(pending)
WAL=WriteAheadLog
