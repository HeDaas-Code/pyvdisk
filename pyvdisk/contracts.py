"""Backend-neutral contracts for the Layer 1 and Layer 2 planes.

These interfaces are additive: existing backends remain valid and adapters may
opt in by satisfying the protocols structurally.
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Optional, Protocol, Tuple


class Capability(str, Enum):
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    ADMIN = "admin"


@dataclass(frozen=True)
class CapabilityGrant:
    """Named, optionally scoped capabilities granted to one execution."""
    name: str
    permissions: frozenset = frozenset()
    scope: str = "/"

    def allows(self, permission: str, scope: Optional[str] = None) -> bool:
        permission_ok = permission in self.permissions or "admin" in self.permissions or Capability.ADMIN in self.permissions
        return permission_ok and (scope is None or scope == self.scope or self.scope == "/")

    def require(self, *permissions: str, scope: Optional[str] = None) -> None:
        missing = [p for p in permissions if not self.allows(p, scope)]
        if missing:
            raise PermissionError(f"{self.name} lacks capability: {', '.join(missing)}")


class DurabilityMode(str, Enum):
    MEMORY = "memory"
    FLUSHED = "flushed"
    SYNCED = "synced"
    REPLICATED = "replicated"


@dataclass(frozen=True)
class Durability:
    """Requested durability; a backend may provide a stronger guarantee."""
    mode: DurabilityMode = DurabilityMode.MEMORY
    replicas: int = 1

    def __post_init__(self) -> None:
        if self.replicas < 1:
            raise ValueError("replicas must be >= 1")
        if self.mode is DurabilityMode.REPLICATED and self.replicas < 2:
            raise ValueError("replicated durability requires at least two replicas")


class BlockDevice(Protocol):
    """Fixed-size block IO contract for Layer 1 StoragePlane."""
    @property
    def block_size(self) -> int: ...
    @property
    def size_bytes(self) -> int: ...
    def read_block(self, index: int) -> bytes: ...
    def write_block(self, index: int, data: bytes, *, durability: Durability = Durability()) -> None: ...
    def flush(self, *, durability: Durability = Durability()) -> None: ...


class NamespaceStore(Protocol):
    def get(self, path: str) -> Optional[Mapping[str, Any]]: ...
    def put(self, path: str, metadata: Mapping[str, Any]) -> None: ...
    def delete(self, path: str, *, recursive: bool = False) -> None: ...
    def list(self, path: str = "/") -> Iterable[str]: ...


class CollectionStore(Protocol):
    def create(self, name: str, *, metadata: Optional[Mapping[str, Any]] = None) -> None: ...
    def drop(self, name: str) -> None: ...
    def put(self, collection: str, key: str, value: Mapping[str, Any], *, durability: Durability = Durability()) -> None: ...
    def get(self, collection: str, key: str) -> Optional[Mapping[str, Any]]: ...
    def scan(self, collection: str) -> Iterable[Tuple[str, Mapping[str, Any]]]: ...


@dataclass(frozen=True)
class Event:
    stream: str
    payload: Mapping[str, Any]
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp_ns: int = field(default_factory=time.time_ns)


class EventStore(Protocol):
    def append(self, event: Event, *, durability: Durability = Durability()) -> str: ...
    def read(self, stream: str, *, after: Optional[str] = None, limit: Optional[int] = None) -> Iterable[Event]: ...


@dataclass
class ExecutionContext:
    """Dependencies and policy supplied to one Layer 2 execution."""
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    capabilities: Tuple[CapabilityGrant, ...] = ()
    durability: Durability = field(default_factory=Durability)
    stores: Mapping[str, Any] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    deadline_ns: Optional[int] = None

    def require(self, permission: str, *, scope: Optional[str] = None) -> None:
        if not any(grant.allows(permission, scope) for grant in self.capabilities):
            raise PermissionError(f"execution {self.run_id} lacks capability: {permission}")

    def expired(self) -> bool:
        return self.deadline_ns is not None and time.time_ns() >= self.deadline_ns


@dataclass
class RunHandle:
    """Minimal observable handle for an execution."""
    run_id: str
    status: str = "pending"
    result: Any = None
    error: Optional[BaseException] = None
    _done: threading.Event = field(default_factory=threading.Event, repr=False, compare=False)

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def complete(self, result: Any = None) -> None:
        with self._lock:
            if self.status == "cancelled":
                return
            self.result, self.error, self.status = result, None, "succeeded"
            self._done.set()

    def fail(self, error: BaseException) -> None:
        with self._lock:
            if self.status == "cancelled":
                return
            self.error, self.status = error, "failed"
            self._done.set()

    def cancel(self) -> bool:
        with self._lock:
            if self._done.is_set():
                return False
            self.status = "cancelled"
            self._done.set()
            return True

    def wait(self, timeout: Optional[float] = None) -> Any:
        if not self._done.wait(timeout):
            raise TimeoutError(f"execution {self.run_id} did not finish")
        if self.error is not None:
            raise self.error
        return self.result


class ExecutionPlane(Protocol):
    def submit(self, operation: Any, context: ExecutionContext) -> RunHandle: ...


__all__ = ["Capability", "CapabilityGrant", "DurabilityMode", "Durability", "BlockDevice", "NamespaceStore", "CollectionStore", "Event", "EventStore", "ExecutionContext", "RunHandle", "ExecutionPlane"]
