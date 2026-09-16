"""Unified checkpoint storage for VFS and host-path backends.

The infrastructure implementation is canonical; pyvdisk.vscript.checkpoint
re-exports this class for compatibility with older VScript users.
"""
from __future__ import annotations
import json
import os
import tempfile
import threading
from pathlib import Path

class CheckpointStore:
    """JSON checkpoints using an explicit VFS or host storage backend."""
    def __init__(self, backend=None, path="/.system/checkpoints.json", *, backend_name=None):
        if backend_name is not None:
            if backend is not None and not isinstance(backend, str):
                raise TypeError("backend and backend_name cannot both select a backend")
            backend = backend_name
        if isinstance(backend, str) and backend in {"vfs", "host"}:
            selected, target = backend, None
        elif backend is None:
            selected, target = None, None
        else:
            selected, target = ("vfs", backend) if hasattr(backend, "read_file") and hasattr(backend, "write_file") else ("host", backend)
        if selected is None:
            raise TypeError("backend must be 'vfs' or 'host', or a VFS object/path")
        self.backend = selected
        if selected == "vfs":
            if target is None:
                raise TypeError("vfs backend requires a VFS object")
            self.vfs, self.path = target, path
        else:
            self.vfs, self.path = None, Path(path if target is None else target)
        self._lock = threading.RLock()
        self.data = self._load()

    @classmethod
    def from_vfs(cls, vfs, path="/.system/checkpoints.json"):
        return cls(vfs, path)
    @classmethod
    def from_host(cls, path):
        return cls(path)

    def _load(self):
        if self.backend == "vfs":
            if not self.vfs.exists(self.path): return {}
            raw, label = self.vfs.read_file(self.path), self.path
        else:
            try: raw, label = self.path.read_bytes(), str(self.path)
            except FileNotFoundError: return {}
        try:
            def _object_hook(value):
                if isinstance(value, dict) and set(value.keys()) == {"__bytes__"}:
                    import base64
                    return base64.b64decode(value["__bytes__"])
                return value
            value = json.loads(raw.decode("utf-8"), object_hook=_object_hook)
            return value if isinstance(value, dict) else {}
        except (ValueError, UnicodeDecodeError, OSError) as exc:
            raise ValueError(f"invalid checkpoint: {label}") from exc

    def get(self, key, default=None):
        with self._lock: return self.data.get(key, default)
    def set(self, key, value):
        with self._lock:
            self.data[key] = value
            self.save()
    def save(self):
        def _default(value):
            if isinstance(value, (bytes, bytearray, memoryview)):
                import base64
                return {"__bytes__": base64.b64encode(bytes(value)).decode("ascii")}
            raise TypeError(f"object of type {type(value).__name__} is not JSON serialisable")
        def _object_hook(value):
            if isinstance(value, dict) and set(value.keys()) == {"__bytes__"}:
                import base64
                return base64.b64decode(value["__bytes__"])
            return value
        raw = json.dumps(self.data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_default).encode("utf-8")
        if self.backend == "vfs":
            self.vfs.write_file(self.path, raw)
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix="." + self.path.name + ".", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def mark_success(self, trigger, event_id):
        self.set(trigger, {"last_event": str(event_id), "status": "success"})
    def last_event(self, trigger):
        value = self.get(trigger, {}) or {}
        return value.get("last_event") if isinstance(value, dict) else None
    def __enter__(self): return self
    def __exit__(self, *args): self.save()
