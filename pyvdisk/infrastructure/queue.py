"""A small, honest, single-process durable work queue.

This is deliberately not a broker: claims are protected by an in-process lock,
and durability is the durability supplied by :class:`CheckpointStore`. Optional
worker threads and lease heartbeats are provided by :mod:`pyvdisk.execution`;
this queue itself does not provide distributed scheduling.
"""
from __future__ import annotations

import copy
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .checkpoint import CheckpointStore


class QueueError(Exception):
    """Base class for queue errors."""


class TaskNotFound(QueueError, KeyError):
    pass


class InvalidTaskState(QueueError):
    pass


class LeaseLost(QueueError):
    pass


@dataclass(frozen=True)
class QueueTask:
    """An immutable snapshot returned by queue operations."""
    id: str
    payload: Any
    status: str
    attempt: int
    idempotency_key: Optional[str] = None
    operation_id: Optional[str] = None
    lease_id: Optional[str] = None
    leased_until: Optional[float] = None
    result: Any = None
    error: Any = None
    dead_letter: bool = False

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "QueueTask":
        return cls(**{key: value.get(key) for key in (
            "id", "payload", "status", "attempt", "idempotency_key", "operation_id",
            "lease_id", "leased_until", "result", "error", "dead_letter")})


class DurableQueue:
    """Durable queue for one process.

    Pass an existing ``CheckpointStore`` (recommended), or ``backend='host'``
    and a checkpoint ``path``.  A VFS store can consequently be used without
    this class knowing anything about its layout.
    """
    KEY = "durable_queue"

    def __init__(self, checkpoint_store=None, *, backend=None, path=None,
                 namespace="durable_queue", max_attempts=3, lease_seconds=60.0,
                 clock=None):
        if isinstance(checkpoint_store, (str, bytes)) and backend is None and path is None:
            path, checkpoint_store = checkpoint_store, None
        if checkpoint_store is None:
            if backend is None or path is None:
                raise TypeError("pass a CheckpointStore, or backend and path")
            checkpoint_store = CheckpointStore(backend=backend, path=path)
        if not isinstance(checkpoint_store, CheckpointStore):
            raise TypeError("checkpoint_store must be a CheckpointStore")
        if max_attempts is not None and max_attempts < 1:
            raise ValueError("max_attempts must be positive or None")
        self.store = checkpoint_store
        self.namespace = namespace
        self.max_attempts = max_attempts
        self.lease_seconds = float(lease_seconds)
        self._clock = clock or time.time
        self._lock = checkpoint_store._lock  # one-process atomicity, not a distributed lock
        with self._lock:
            if not isinstance(self.store.get(self.namespace), dict):
                self.store.set(self.namespace, {"tasks": {}, "idempotency": {}, "next_sequence": 0})

    def _state(self):
        value = self.store.get(self.namespace, {})
        return value if isinstance(value, dict) else {"tasks": {}, "idempotency": {}}

    def _save(self, state):
        self.store.set(self.namespace, state)

    @staticmethod
    def _copy(value):
        return copy.deepcopy(value)

    def _task(self, state, task_id):
        value = state["tasks"].get(task_id)
        if value is None:
            raise TaskNotFound(task_id)
        return value

    def _result(self, value):
        return QueueTask.from_dict(self._copy(value))

    def enqueue(self, payload, idempotency_key=None, *, task_id=None, operation_id=None):
        """Persist a queued task; repeated keys return the same durable operation."""
        with self._lock:
            state = self._state()
            if idempotency_key is not None:
                old_id = state["idempotency"].get(str(idempotency_key))
                if old_id is not None:
                    return self._result(self._task(state, old_id))
            task_id = str(task_id or uuid.uuid4())
            if task_id in state["tasks"]:
                raise QueueError("task id already exists: %s" % task_id)
            sequence = int(state.get("next_sequence", 0))
            state["next_sequence"] = sequence + 1
            operation_id = str(operation_id or (payload.get("operation_id") if isinstance(payload, dict) else uuid.uuid4().hex))
            task = {"id": task_id, "sequence": sequence, "payload": self._copy(payload), "status": "queued",
                    "attempt": 0, "idempotency_key": idempotency_key, "operation_id": operation_id,
                    "lease_id": None, "leased_until": None, "result": None,
                    "error": None, "dead_letter": False}
            state["tasks"][task_id] = task
            if idempotency_key is not None:
                state["idempotency"][str(idempotency_key)] = task_id
            self._save(state)
            return self._result(task)

    def claim(self, *, lease_seconds=None, now=None):
        """Claim the oldest queued task and increment its attempt number."""
        with self._lock:
            self.recover_stale(now=now)
            state = self._state()
            candidates = [t for t in state["tasks"].values() if t["status"] == "queued"]
            if not candidates:
                return None
            task = min(candidates, key=lambda t: (t.get("sequence", 0), t["id"]))
            current = self._clock() if now is None else float(now)
            task["status"] = "running"
            task["attempt"] += 1
            task["lease_id"] = str(uuid.uuid4())
            task["leased_until"] = current + (self.lease_seconds if lease_seconds is None else float(lease_seconds))
            self._save(state)
            return self._result(task)

    def _running(self, state, task_id, lease_id=None):
        task = self._task(state, task_id)
        if task["status"] != "running":
            raise InvalidTaskState("%s is %s" % (task_id, task["status"]))
        if lease_id is not None and lease_id != task["lease_id"]:
            raise LeaseLost(task_id)
        return task

    def heartbeat(self, task_id, *, lease_id, lease_seconds=None, now=None):
        """Extend a running task lease, rejecting stale workers."""
        with self._lock:
            state = self._state()
            task = self._running(state, self._id(task_id), lease_id)
            current = self._clock() if now is None else float(now)
            task["leased_until"] = current + (self.lease_seconds if lease_seconds is None else float(lease_seconds))
            self._save(state)
            return self._result(task)

    renew = heartbeat

    def complete(self, task_id, result=None, *, lease_id=None):
        with self._lock:
            state = self._state(); task = self._running(state, self._id(task_id), lease_id)
            task.update(status="succeeded", result=self._copy(result), lease_id=None, leased_until=None)
            self._save(state); return self._result(task)

    def fail(self, task_id, error=None, *, retry=False, lease_id=None):
        with self._lock:
            state = self._state(); task = self._running(state, self._id(task_id), lease_id)
            task["error"] = self._copy(error)
            should_retry = retry and (self.max_attempts is None or task["attempt"] < self.max_attempts)
            task.update(status="queued" if should_retry else "failed", lease_id=None, leased_until=None,
                        dead_letter=not should_retry and retry)
            self._save(state); return self._result(task)

    def retry(self, task_id):
        with self._lock:
            state = self._state(); task = self._task(state, self._id(task_id))
            if task["status"] != "failed": raise InvalidTaskState("task is not failed")
            task.update(status="queued", dead_letter=False, lease_id=None, leased_until=None)
            self._save(state); return self._result(task)

    def dead_letter(self, task_id, error=None):
        with self._lock:
            state = self._state(); task = self._task(state, self._id(task_id))
            if task["status"] not in ("failed", "running"): raise InvalidTaskState("task cannot be dead-lettered")
            task.update(status="failed", dead_letter=True, lease_id=None, leased_until=None)
            if error is not None: task["error"] = self._copy(error)
            self._save(state); return self._result(task)

    def cancel(self, task_id):
        with self._lock:
            state = self._state(); task = self._task(state, self._id(task_id))
            if task["status"] not in ("queued", "running"): raise InvalidTaskState("task cannot be cancelled")
            task.update(status="cancelled", lease_id=None, leased_until=None)
            self._save(state); return self._result(task)

    def recover_stale(self, *, now=None):
        """Requeue expired claims, or dead-letter them at the attempt limit."""
        with self._lock:
            state = self._state(); current = self._clock() if now is None else float(now); changed = []
            for task in state["tasks"].values():
                if task["status"] == "running" and task["leased_until"] is not None and task["leased_until"] <= current:
                    if self.max_attempts is not None and task["attempt"] >= self.max_attempts:
                        task.update(status="failed", dead_letter=True)
                    else:
                        task.update(status="queued")
                    task.update(lease_id=None, leased_until=None); changed.append(self._result(task))
            if changed: self._save(state)
            return changed

    def get(self, task_id):
        with self._lock: return self._result(self._task(self._state(), self._id(task_id)))

    @staticmethod
    def _id(task):
        return task.id if isinstance(task, QueueTask) else str(task)

    def list(self, status=None):
        with self._lock:
            values = self._state()["tasks"].values()
            return [self._result(t) for t in values if status is None or t["status"] == status]


PersistentQueue = DurableQueue
Queue = DurableQueue
