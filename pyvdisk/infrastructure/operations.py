"""Persisted operation registry for cross-process queued execution (Issue #1 B1).

The queue's payload only carries the operation *id*; this module persists the
operation body (callable reference, vscript source, or arbitrary payload dict)
so a worker process can resume work without the original caller's frame.

Storage backends
================
* A :class:`CheckpointStore` (or any object exposing ``get``/``set`` with a
  dict payload) — records are written under the ``operations`` namespace.
* A host directory (``str``/``Path``) — each operation becomes
  ``<dir>/<op_id>.json``.
* ``None`` — the registry is in-memory only; useful for tests.

Cross-process semantics
=======================
* A normal ``def`` is persisted as ``kind="callable"`` with ``payload.name``
  holding ``module:qualname``. A worker imports the module and looks up the
  function; a missing target raises :class:`OperationError` with a clear
  message rather than a generic ``NoneType`` error.
* A :class:`str` (VScript source) or ``Program`` is persisted as
  ``kind="vscript"`` with the original source string; the worker compiles it.
* A :class:`dict` is persisted as ``kind="payload"``; the worker returns the
  dict directly.
* Lambdas and local ``def`` fail to persist (no ``module:qualname``) — the
  caller falls back to in-memory delivery, matching the legacy behaviour.
"""
from __future__ import annotations

import importlib
import inspect
import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union


class OperationError(RuntimeError):
    """Base class for registry errors."""


class OperationNotFound(OperationError, KeyError):
    """The requested operation has no record on disk."""


class UnserializableOperation(OperationError):
    """The operation cannot be persisted (e.g. lambda / local def)."""


@dataclass(frozen=True)
class OperationRecord:
    op_id: str
    kind: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        return {"op_id": self.op_id, "kind": self.kind, "payload": self.payload}

    @classmethod
    def from_json(cls, value: Dict[str, Any]) -> "OperationRecord":
        return cls(
            op_id=str(value.get("op_id") or value.get("op_id") or ""),
            kind=str(value.get("kind") or ""),
            payload=dict(value.get("payload") or {}),
        )


_CALLABLES: Dict[str, Callable[..., Any]] = {}
_CALLABLES_LOCK = threading.Lock()


def register_callable(name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
    """Register a function under a stable ``module:qualname``-style key.

    The key is the function's natural ``module:qualname`` when available; a
    caller may pass an explicit override (used for tests).
    """
    if not name:
        module = getattr(fn, "__module__", None) or "_local_"
        qual = getattr(fn, "__qualname__", None) or repr(fn)
        name = f"{module}:{qual}"
    with _CALLABLES_LOCK:
        _CALLABLES[name] = fn
    return fn


def registered_callables() -> Dict[str, Callable[..., Any]]:
    with _CALLABLES_LOCK:
        return dict(_CALLABLES)


def _clear_callables() -> None:
    """Test hook: drop the in-process registry."""
    with _CALLABLES_LOCK:
        _CALLABLES.clear()


def _name_of(fn: Callable[..., Any]) -> Optional[str]:
    module = getattr(fn, "__module__", None)
    qual = getattr(fn, "__qualname__", None)
    if not module or not qual:
        return None
    if qual.startswith("<lambda") or "<locals>" in qual:
        return None
    return f"{module}:{qual}"


class RegisteredCallable:
    """A bound callable that knows its registered name and arguments."""

    __slots__ = ("name", "target", "args", "kwargs")

    def __init__(self, name: str, target: Callable[..., Any], args: tuple = (), kwargs: Optional[dict] = None):
        self.name = name
        self.target = target
        self.args = tuple(args)
        self.kwargs = dict(kwargs or {})

    def __call__(self, *extra, **ex_kw):
        if extra or ex_kw:
            return self.target(*self.args, *extra, **{**self.kwargs, **ex_kw})
        return self.target(*self.args, **self.kwargs)


def _describe_callable(fn: Callable[..., Any], args: tuple = (), kwargs: Optional[dict] = None) -> Dict[str, Any]:
    name = _name_of(fn)
    if not name:
        raise UnserializableOperation("callable lacks module:qualname (lambda or local def)")
    return {
        "name": name,
        "args": list(args),
        "kwargs": dict(kwargs or {}),
    }


def _describe_vscript(value: Any) -> Dict[str, Any]:
    source = value.source if hasattr(value, "source") and value.source else (value if isinstance(value, str) else None)
    if source is None:
        raise UnserializableOperation("vscript record requires a string source or compiled Program")
    return {"source": str(source)}


def _describe_payload(value: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise UnserializableOperation("payload kind requires a dict")
    return dict(value)


def describe_operation(value: Any) -> Dict[str, Any]:
    """Return a JSON-serialisable {kind, payload} dict for the given value.

    Raises :class:`UnserializableOperation` for kinds we cannot persist.
    """
    if isinstance(value, str):
        return {"kind": "vscript", "payload": _describe_vscript(value)}
    if callable(value):
        return {"kind": "callable", "payload": _describe_callable(value)}
    if isinstance(value, dict):
        return {"kind": "payload", "payload": _describe_payload(value)}
    if hasattr(value, "ast"):
        return {"kind": "vscript", "payload": _describe_vscript(value)}
    raise UnserializableOperation(f"unsupported operation type: {type(value).__name__}")


class OperationRegistry:
    """Persistent registry of operations keyed by ``op_id``."""

    NAMESPACE = "operations"

    def __init__(self, store=None, *, host_dir: Optional[Union[str, Path]] = None, namespace: str = NAMESPACE):
        self._lock = threading.RLock()
        self._namespace = str(namespace)
        self._host_dir: Optional[Path] = None
        self._store = None
        if host_dir is not None:
            self._host_dir = Path(host_dir)
            self._host_dir.mkdir(parents=True, exist_ok=True)
        elif store is not None:
            self._store = store
        if self._store is None and self._host_dir is None:
            self._memory: Dict[str, Dict[str, Any]] = {}
        else:
            self._memory = None

    @property
    def backend(self) -> str:
        if self._host_dir is not None:
            return "host"
        if self._store is not None:
            return "store"
        return "memory"

    def has(self, op_id: str) -> bool:
        with self._lock:
            return self._raw_get(op_id) is not None

    def load(self, op_id: str) -> OperationRecord:
        with self._lock:
            raw = self._raw_get(op_id)
        if raw is None:
            raise OperationNotFound(op_id)
        return OperationRecord.from_json(raw)

    def recover(self, op_id: str) -> Any:
        """Return a Python value usable by :class:`ExecutionService`."""
        record = self.load(op_id)
        if record.kind == "callable":
            name = record.payload.get("name")
            if not name:
                raise OperationError(f"callable record {op_id!r} missing name")
            fn = self._resolve_callable(name)
            args = tuple(record.payload.get("args") or ())
            kwargs = dict(record.payload.get("kwargs") or {})
            return RegisteredCallable(name, fn, args, kwargs)
        if record.kind == "vscript":
            return record.payload.get("source")
        if record.kind == "payload":
            return dict(record.payload)
        raise OperationError(f"unknown operation kind: {record.kind!r}")

    def save(self, op_id: str, kind: str, payload: Dict[str, Any]) -> OperationRecord:
        record = OperationRecord(op_id=op_id, kind=str(kind), payload=dict(payload))
        with self._lock:
            self._raw_put(record.to_json())
        return record

    def forget(self, op_id: str) -> bool:
        with self._lock:
            if self._host_dir is not None:
                path = self._host_dir / f"{op_id}.json"
                if path.exists():
                    path.unlink()
                    return True
                return False
            if self._store is not None:
                ns = self._store.get(self._namespace) or {}
                if op_id in ns:
                    ns.pop(op_id, None)
                    self._store.set(self._namespace, ns)
                    return True
                return False
            if self._memory is not None and op_id in self._memory:
                self._memory.pop(op_id, None)
                return True
            return False

    def _raw_get(self, op_id: str) -> Optional[Dict[str, Any]]:
        if self._host_dir is not None:
            path = self._host_dir / f"{op_id}.json"
            if not path.exists():
                return None
            try:
                with path.open("r", encoding="utf-8") as fh:
                    value = json.load(fh)
            except (OSError, ValueError) as exc:
                raise OperationError(f"operation record {op_id!r} unreadable: {exc}") from exc
            return value if isinstance(value, dict) else None
        if self._store is not None:
            ns = self._store.get(self._namespace) or {}
            if not isinstance(ns, dict):
                return None
            value = ns.get(op_id)
            return value if isinstance(value, dict) else None
        if self._memory is not None:
            value = self._memory.get(op_id)
            return value if isinstance(value, dict) else None
        return None

    def _raw_put(self, value: Dict[str, Any]) -> None:
        if self._host_dir is not None:
            op_id = str(value.get("op_id") or "")
            if not op_id:
                raise OperationError("operation record missing op_id")
            path = self._host_dir / f"{op_id}.json"
            tmp = path.with_suffix(".json.tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(value, fh, ensure_ascii=False, default=str)
            os.replace(tmp, path)
            return
        if self._store is not None:
            ns = self._store.get(self._namespace) or {}
            if not isinstance(ns, dict):
                ns = {}
            ns[str(value.get("op_id"))] = value
            self._store.set(self._namespace, ns)
            return
        if self._memory is not None:
            self._memory[str(value.get("op_id"))] = value

    def _resolve_callable(self, name: str) -> Callable[..., Any]:
        if ":" not in name:
            raise OperationError(f"callable name must be module:qualname, got {name!r}")
        module_name, _, qual = name.partition(":")
        target = registered_callables().get(name)
        if target is not None:
            return target
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise OperationError(f"callable {name!r} not importable: {exc}") from exc
        obj: Any = module
        for part in qual.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                break
        if obj is None:
            raise OperationError(f"callable {name!r} not present in module {module_name!r}")
        register_callable(name, obj)
        return obj


__all__ = [
    "OperationError",
    "OperationNotFound",
    "UnserializableOperation",
    "OperationRecord",
    "OperationRegistry",
    "RegisteredCallable",
    "register_callable",
    "registered_callables",
    "describe_operation",
]
