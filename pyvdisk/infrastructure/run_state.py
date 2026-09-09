"""Durable synchronous execution run state over canonical CheckpointStore."""
from __future__ import annotations
import threading, time, uuid
from dataclasses import dataclass, asdict
from typing import Any, Optional

class RunStateConflict(RuntimeError):
    """Optimistic concurrency or invalid state transition."""

@dataclass
class RunRecord:
    run_id: str
    status: str = "pending"
    attempt: int = 0
    created_at_ns: int = 0
    started_at_ns: Optional[int] = None
    finished_at_ns: Optional[int] = None
    updated_at_ns: int = 0
    result_ref: Any = None
    error_ref: Any = None
    idempotency_key: Optional[str] = None
    version: int = 0
    def __post_init__(self):
        if not self.created_at_ns: self.created_at_ns = time.time_ns()
        if not self.updated_at_ns: self.updated_at_ns = self.created_at_ns

class RunStateStore:
    ROOT = "__run_records__"
    STATES = {"pending", "running", "succeeded", "failed", "cancelled"}
    TERMINAL = {"succeeded", "failed", "cancelled"}
    def __init__(self, checkpoint_store):
        self.checkpoints, self._lock = checkpoint_store, threading.RLock()
    @classmethod
    def from_data_disk(cls, data_disk):
        if not data_disk.mounted: data_disk.mount()
        return cls(data_disk.checkpoints)
    def _all(self):
        value = self.checkpoints.get(self.ROOT, {})
        return dict(value) if isinstance(value, dict) else {}
    def _record(self, run_id):
        raw = self._all().get(run_id)
        return RunRecord(**raw) if raw else None
    def get(self, run_id):
        with self._lock: return self._record(run_id)
    def list(self, *, status=None):
        with self._lock:
            out = [RunRecord(**v) for v in self._all().values()]
            return [r for r in out if status is None or r.status == status]
    def create(self, run_id=None, *, idempotency_key=None):
        run_id = run_id or uuid.uuid4().hex
        with self._lock:
            records = self._all(); existing = self._record(run_id)
            if existing: return existing
            if idempotency_key:
                for raw in records.values():
                    if raw.get("idempotency_key") == idempotency_key: return RunRecord(**raw)
            record = RunRecord(run_id=run_id, idempotency_key=idempotency_key)
            records[run_id] = asdict(record); self.checkpoints.set(self.ROOT, records)
            return record
    def transition(self, run_id, status, *, expected_version=None, result_ref=None, error_ref=None):
        if status not in self.STATES: raise ValueError("unknown run state: " + status)
        with self._lock:
            records = self._all(); record = self._record(run_id)
            if record is None: raise KeyError(run_id)
            if expected_version is not None and record.version != expected_version: raise RunStateConflict("run version changed")
            allowed = {"pending": {"running", "cancelled"}, "running": self.TERMINAL | {"pending"}, "succeeded": set(), "failed": {"pending"}, "cancelled": set()}
            if status not in allowed[record.status]: raise RunStateConflict(f"invalid transition {record.status}->{status}")
            now = time.time_ns(); record.status, record.updated_at_ns, record.version = status, now, record.version + 1
            if status == "running": record.attempt += 1; record.started_at_ns = now
            if status in self.TERMINAL: record.finished_at_ns = now
            if status == "succeeded": record.result_ref, record.error_ref = result_ref, None
            if status == "failed": record.error_ref, record.result_ref = error_ref, None
            records[run_id] = asdict(record); self.checkpoints.set(self.ROOT, records)
            return record
    def recover_stale(self, max_age_seconds=3600, *, to="pending"):
        if to not in {"pending", "failed"}: raise ValueError("to must be pending or failed")
        cutoff = time.time_ns() - int(max_age_seconds * 1_000_000_000); recovered = []
        with self._lock:
            records = self._all()
            for run_id, raw in list(records.items()):
                if raw.get("status") == "running" and raw.get("updated_at_ns", 0) <= cutoff:
                    record = RunRecord(**raw); now = time.time_ns(); record.status, record.updated_at_ns, record.version = to, now, record.version + 1
                    if to == "failed": record.finished_at_ns, record.error_ref = now, "stale running execution recovered"
                    records[run_id] = asdict(record); recovered.append(record)
            if recovered: self.checkpoints.set(self.ROOT, records)
        return recovered
__all__ = ["RunRecord", "RunStateStore", "RunStateConflict"]
