"""Structured audit records for VScript executions.

The module deliberately has no storage dependency: applications can provide a
callable or an object with an emit method to Runtime.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Mapping, Optional


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def script_hash(source: Any) -> str:
    """Return a stable SHA-256 digest for script source or an AST fallback."""
    if isinstance(source, str):
        data = source.encode("utf-8")
    elif isinstance(source, bytes):
        data = source
    else:
        data = repr(source).encode("utf-8")
    return _sha256(data)


def policy_hash(policy: Any) -> str:
    """Hash a policy public dataclass fields in canonical JSON form."""
    values = asdict(policy) if hasattr(policy, "__dataclass_fields__") else vars(policy)
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return _sha256(encoded)


@dataclass(frozen=True)
class AuditRecord:
    run_id: str
    script_hash: str
    policy_hash: str
    status: str
    metrics: Mapping[str, Any]
    error: Optional[Mapping[str, str]] = None
    started_at: float = 0.0
    finished_at: float = 0.0
    # Execution-plane correlation fields.  All are optional for old callers.
    task_id: Optional[str] = None
    attempt: Optional[int] = None
    queue_id: Optional[str] = None
    checkpoint_ref: Optional[str] = None
    capability_summary: Optional[Mapping[str, Any]] = None
    parent_run_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class CheckpointAuditSink:
    """Small durable sink backed by a CheckpointStore list (not immutable)."""
    def __init__(self, store, key="__audit_records__"):
        self.store, self.key = store, key

    def emit(self, record):
        value = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        rows = self.store.get(self.key, [])
        self.store.set(self.key, list(rows) + [value])

    def records(self):
        return tuple(self.store.get(self.key, []) or [])


class DataDiskAuditSink:
    """Persist audit records in a DataDisk structured-log stream.

    This provides storage durability supplied by the backend; it does not claim
    tamper resistance or immutability.
    """
    def __init__(self, disk, stream="audit"):
        self.disk = disk.logs if hasattr(disk, "logs") else disk
        self.stream = stream
        if hasattr(self.disk, "list_streams") and not any(
            (item == stream or (isinstance(item, dict) and item.get("name") == stream))
            for item in self.disk.list_streams()
        ):
            self.disk.create_stream(stream)

    def emit(self, record):
        from ..logging_core import LogEvent
        value = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        self.disk.append(self.stream, LogEvent(time.time_ns(), "INFO", "pyvdisk.audit", "audit_record", fields=value))


AuditSink = CheckpointAuditSink
PersistentAuditSink = CheckpointAuditSink


def new_run_id() -> str:
    return str(uuid.uuid4())


def monotonic_ms(start: float) -> float:
    return round((time.monotonic() - start) * 1000, 3)
