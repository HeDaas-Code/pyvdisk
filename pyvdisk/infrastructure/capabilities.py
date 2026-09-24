"""Opt-in capability-scoped views over DataDisk namespaces."""
from __future__ import annotations
from typing import Any
from ..contracts import ExecutionContext


def _path(value: Any) -> str:
    value = str(value)
    # Keep authorization and backend path parsing in the same safe domain.
    # VFS paths are POSIX paths; accepting NUL or backslashes would allow
    # platform/backend-specific reinterpretation after the scope check.
    if "\x00" in value or "\\" in value:
        raise PermissionError("capability scope contains an invalid path character")
    if not value.startswith("/"): 
        value = "/" + value
    parts = [p for p in value.split("/") if p not in ("", ".")]
    if ".." in parts:
        raise PermissionError("capability scope cannot contain '..'")
    return "/" + "/".join(parts) if parts else "/"


def _inside(value: Any, scope: str) -> bool:
    value, scope = _path(value), _path(scope)
    return scope == "/" or value == scope or value.startswith(scope.rstrip("/") + "/")


class CapabilityNamespace:
    """Base guarded adapter; unknown methods are never forwarded."""
    def __init__(self, target: Any, context: ExecutionContext, name: str):
        self._target, self.context, self.name = target, context, name

    def _check(self, permission: str, scope: Any = "/") -> None:
        requested = _path(scope)
        for grant in self.context.capabilities:
            raw_name = grant.name
            names = {str(raw_name).lower(), str(getattr(raw_name, "value", "")).lower()}
            if not ({self.name, "*"} & names):
                continue
            permissions = {str(p).lower() for p in grant.permissions}
            permissions.update(getattr(p, "value", "").lower() for p in grant.permissions)
            if (permission.lower() in permissions or "admin" in permissions) and _inside(requested, grant.scope):
                return
        raise PermissionError(f"execution {self.context.run_id} lacks {self.name}:{permission} for {requested}")

    def _call(self, permission: str, method: str, *args, scope="/", **kwargs):
        self._check(permission, scope)
        return getattr(self._target, method)(*args, **kwargs)


class ScopedFileNamespace(CapabilityNamespace):
    _PROTECTED = ("/.vectors", "/.logs", "/.system/wal.jsonl", "/.system/wal.ckpt.json", "/.system/checkpoint.json")

    def _check_file(self, permission, path):
        normalized = _path(path)
        if any(normalized == root or normalized.startswith(root + "/") for root in self._PROTECTED):
            raise PermissionError("capability cannot access protected DataDisk internals")
        self._check(permission, normalized)

    def exists(self, path): self._check_file("read", path); return self._target.exists(path)
    def isfile(self, path): self._check_file("read", path); return self._target.isfile(path)
    def isdir(self, path): self._check_file("read", path); return self._target.isdir(path)
    def listdir(self, path="/"): self._check_file("read", path); return self._target.listdir(path)
    def stat(self, path, follow=True): self._check_file("read", path); return self._target.stat(path, follow)
    def read_file(self, path): self._check_file("read", path); return self._target.read_file(path)
    def open(self, path, mode="rb"):
        permission = "write" if any(x in mode for x in "wxa+") else "read"
        self._check_file(permission, path); return self._target.open(path, mode)
    def mkdir(self, path, mode=0o755): self._check_file("write", path); return self._target.mkdir(path, mode)
    def makedirs(self, path, mode=0o755): self._check_file("write", path); return self._target.makedirs(path, mode)
    def write_file(self, path, data, mode=0o644): self._check_file("write", path); return self._target.write_file(path, data, mode)
    def append_file(self, path, data): self._check_file("write", path); return self._target.append_file(path, data)
    def remove(self, path): self._check_file("delete", path); return self._target.remove(path)
    def rmtree(self, path): self._check_file("delete", path); return self._target.rmtree(path)
    def rename(self, src, dst):
        self._check_file("write", src); self._check_file("write", dst); return self._target.rename(src, dst)
    def walk(self, top="/"): self._check_file("read", top); return self._target.walk(top)
    def statfs(self): self._check("read"); return self._target.statfs()
    def df(self): self._check("read"); return self._target.df()
    def du(self, path="/"): self._check_file("read", path); return self._target.du(path)
    def fsck(self, repair=False): return self._call("admin" if repair else "read", "fsck", repair, scope="/")


class ScopedVectorNamespace(CapabilityNamespace):
    def _scope(self, collection):
        value = str(collection)
        if not value or value in (".", "..") or "/" in value or "\\" in value or "\x00" in value:
            raise PermissionError("collection scope must be a single safe name")
        return "/" + value
    def create_collection(self, name, *args, **kwargs): return self._call("admin", "create_collection", name, *args, scope=self._scope(name), **kwargs)
    def list_collections(self):
        self._check("read")
        return [name for name in self._target.list_collections() if self._allowed_name(name)]
    def _allowed_name(self, name):
        try: self._check("read", self._scope(name)); return True
        except PermissionError: return False
    def drop_collection(self, name): return self._call("admin", "drop_collection", name, scope=self._scope(name))
    def upsert(self, collection, *args, **kwargs): return self._call("write", "upsert", collection, *args, scope=self._scope(collection), **kwargs)
    def upsert_many(self, collection, *args, **kwargs): return self._call("write", "upsert_many", collection, *args, scope=self._scope(collection), **kwargs)
    def get(self, collection, *args, **kwargs): return self._call("read", "get", collection, *args, scope=self._scope(collection), **kwargs)
    def delete(self, collection, *args, **kwargs): return self._call("delete", "delete", collection, *args, scope=self._scope(collection), **kwargs)
    def count(self, collection, *args, **kwargs): return self._call("read", "count", collection, *args, scope=self._scope(collection), **kwargs)
    def search(self, collection, *args, **kwargs): return self._call("read", "search", collection, *args, scope=self._scope(collection), **kwargs)


class ScopedLogNamespace(CapabilityNamespace):
    def _scope(self, stream):
        value = str(stream)
        if not value or value in (".", "..") or "/" in value or "\\" in value or "\x00" in value:
            raise PermissionError("stream scope must be a single safe name")
        return "/" + value
    def create_stream(self, name, *args, **kwargs): return self._call("admin", "create_stream", name, *args, scope=self._scope(name), **kwargs)
    def list_streams(self):
        self._check("read")
        return [name for name in self._target.list_streams() if self._allowed_name(name)]
    def _allowed_name(self, name):
        try: self._check("read", self._scope(name)); return True
        except PermissionError: return False
    def drop_stream(self, name): return self._call("admin", "drop_stream", name, scope=self._scope(name))
    def append(self, stream, *args, **kwargs): return self._call("append", "append", stream, *args, scope=self._scope(stream), **kwargs)
    def append_many(self, stream, *args, **kwargs): return self._call("append", "append_many", stream, *args, scope=self._scope(stream), **kwargs)
    def query(self, stream, *args, **kwargs): return self._call("read", "query", stream, *args, scope=self._scope(stream), **kwargs)
    def count(self, stream, *args, **kwargs): return self._call("read", "count", stream, *args, scope=self._scope(stream), **kwargs)
    def tail(self, stream, *args, **kwargs): return self._call("read", "tail", stream, *args, scope=self._scope(stream), **kwargs)
    def follow(self, stream, *args, **kwargs): return self._call("read", "follow", stream, *args, scope=self._scope(stream), **kwargs)
    def stats(self, stream, *args, **kwargs): return self._call("read", "stats", stream, *args, scope=self._scope(stream), **kwargs)
    def enforce_retention(self, stream): return self._call("admin", "enforce_retention", stream, scope=self._scope(stream))
    def compact(self, stream): return self._call("admin", "compact", stream, scope=self._scope(stream))


class ScopedCheckpointNamespace(CapabilityNamespace):
    def get(self, key, default=None): return self._call("read", "get", key, default, scope="/" + str(key))
    def set(self, key, value): return self._call("write", "set", key, value, scope="/" + str(key))
    def save(self): return self._call("write", "save", scope="/")
    def mark_success(self, trigger, event_id): return self._call("write", "mark_success", trigger, event_id, scope="/" + str(trigger))
    def last_event(self, trigger): return self._call("read", "last_event", trigger, scope="/" + str(trigger))


class ScopedDataDisk:
    """Opt-in capability view; the regular DataDisk API is unchanged."""
    def __init__(self, disk, context: ExecutionContext):
        # Do not expose the unrestricted disk through the capability view.
        # Callers must use the explicitly guarded namespace adapters.
        self._disk, self.context = disk, context
        self.fs = ScopedFileNamespace(disk.fs, context, "fs")
        self.vector = self.vectors = ScopedVectorNamespace(disk.vector, context, "vector")
        self.log = self.logs = ScopedLogNamespace(disk.log, context, "log")
        self.checkpoints = ScopedCheckpointNamespace(disk.checkpoints, context, "checkpoint")
    def __enter__(self): self._disk.mount(); return self
    def __exit__(self, *exc): self._disk.close()
    @property
    def mounted(self): return bool(getattr(self._disk, "mounted", False))
    @property
    def path(self): return getattr(self._disk, "path", None)


def scoped(disk, context):
    if not getattr(disk, "mounted", False):
        raise RuntimeError("DataDisk must be mounted before creating a scoped view")
    return ScopedDataDisk(disk, context)

scoped_data_disk = scoped

__all__ = ["CapabilityNamespace", "ScopedDataDisk", "ScopedFileNamespace", "ScopedVectorNamespace", "ScopedLogNamespace", "ScopedCheckpointNamespace", "scoped", "scoped_data_disk"]