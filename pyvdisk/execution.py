"""Small synchronous ExecutionPlane implementation.

This adapter deliberately runs inline and never claims concurrency.
"""
from __future__ import annotations
import inspect
import uuid
import threading
import time
from dataclasses import replace
from typing import Any, Callable, Optional
from .contracts import ExecutionContext, RunHandle
from .infrastructure import DataDisk, RunStateStore, DurableQueue
from .vscript import Compiler, Runtime
from .vscript.policy import Policy, Capability as VScriptCapability
from .vscript.stdlib import Handle

class ExecutionService:
    """Synchronous adapter joining DataDisk, VScript Runtime and contracts."""
    def __init__(self, data_disk: Optional[Any] = None, *, policy: Optional[Policy] = None,
                 runtime_factory: Callable[..., Runtime] = Runtime, queue=None,
                 checkpoint_store=None, run_state=None, audit_sink=None,
                 operations=None):
        """Create a synchronous execution service.

        Queue-driven work is explicitly opt-in and driven by run_next/poll_once
        in the calling thread. It provides single-process checkpoint durability,
        not distributed execution. Existing submit/run behavior is unchanged.
        """
        self.data_disk = data_disk
        self.policy = policy or Policy()
        self.runtime_factory = runtime_factory
        self.run_state = run_state
        self.audit_sink = audit_sink
        if queue is not None and checkpoint_store is not None:
            raise TypeError("pass queue or checkpoint_store, not both")
        if checkpoint_store is not None:
            from .infrastructure import CheckpointStore
            queue = DurableQueue(checkpoint_store)
        if queue is not None and not isinstance(queue, DurableQueue):
            raise TypeError("queue must be a DurableQueue")
        self.queue = queue
        self._queued_operations = {}
        self._queued_contexts = {}
        self._queued_handles = {}
        self._workers = []
        self._worker_stop = None
        from .infrastructure.operations import OperationRegistry
        self.operations = operations
        if self.operations is None and self.queue is not None:
            store = getattr(self.queue, "store", None)
            if store is not None:
                self.operations = OperationRegistry(store=store)

    @property
    def worker_count(self):
        return sum(t.is_alive() for t in self._workers)

    def start_workers(self, count=1, *, poll_interval=0.05, lease_seconds=None):
        if self.queue is None:
            raise RuntimeError("queued execution is not configured")
        if count < 1:
            raise ValueError("count must be positive")
        if self._worker_stop is None:
            self._worker_stop = threading.Event()
        for index in range(int(count)):
            thread = threading.Thread(target=self._worker_loop, args=(self._worker_stop, float(poll_interval), lease_seconds), daemon=True)
            self._workers.append(thread)
            thread.start()
        return self

    start_worker = start_workers

    def _worker_loop(self, stop, poll_interval, lease_seconds):
        while not stop.is_set():
            try:
                result = self.run_next(lease_seconds=lease_seconds)
                if result is None: stop.wait(poll_interval)
            except Exception:
                stop.wait(poll_interval)

    def stop_workers(self, *, wait=True, timeout=None):
        if self._worker_stop is None: return
        self._worker_stop.set()
        if wait:
            for thread in self._workers: thread.join(timeout)
        self._workers = [t for t in self._workers if t.is_alive()]
        if not self._workers: self._worker_stop = None

    stop_worker = stop_workers

    def enqueue_async(self, operation, context=None, *, idempotency_key=None, task_id=None):
        context = context or ExecutionContext()
        task = self.enqueue_operation(operation, context, idempotency_key=idempotency_key, task_id=task_id)
        handle = self._queued_handles.get(task.id)
        if handle is None:
            handle = RunHandle(context.run_id)
            self._queued_handles[task.id] = handle
        return handle

    submit_async = enqueue_async

    def _disk(self):
        disk = self.data_disk
        if disk is None: return None
        if isinstance(disk, (str, bytes)):
            disk = DataDisk(disk); self.data_disk = disk
        if hasattr(disk, "mount") and not getattr(disk, "mounted", False): disk.mount()
        return disk

    def _policy(self, context):
        candidate = context.metadata.get("policy")
        return candidate if isinstance(candidate, Policy) else self.policy

    @staticmethod
    def _scoped_view(disk, context):
        if disk is None:
            return None
        from .infrastructure.capabilities import scoped_data_disk
        return scoped_data_disk(disk, context)

    @staticmethod
    def _call(operation, context, disk):
        try: parameters = inspect.signature(operation).parameters
        except (TypeError, ValueError):
            view = ExecutionService._scoped_view(disk, context)
            return operation(context, view if view is not None else disk)
        if any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in parameters.values()) or len(parameters) >= 2:
            view = ExecutionService._scoped_view(disk, context)
            return operation(context, view if view is not None else disk)
        if len(parameters) == 1: return operation(context)
        return operation()

    def _script(self, operation, context, disk):
        compiler = Compiler()
        program = compiler.compile(operation) if isinstance(operation, str) else operation
        if not hasattr(program, "ast"): raise TypeError("operation must be callable, VScript source, or compiled Program")
        bindings = {}
        if disk is not None:
            permissions = set()
            for grant in context.capabilities:
                permissions.update(str(p.value if hasattr(p, "value") else p) for p in grant.permissions)
            bindings["disk"] = Handle(VScriptCapability("data", "fs", frozenset(permissions or {"read"}), disk.fs))
        audit_context = {"task_id": context.metadata.get("task_id"), "attempt": context.metadata.get("attempt"), "queue_id": context.metadata.get("queue_id"), "checkpoint_ref": context.metadata.get("checkpoint_ref"), "capability_summary": {g.name: sorted(str(p.value if hasattr(p, "value") else p) for p in g.permissions) for g in context.capabilities}, "parent_run_id": context.metadata.get("parent_run_id")}
        audit_context = {k: v for k, v in audit_context.items() if v is not None}
        runtime = self.runtime_factory(policy=self._policy(context), compiler=compiler, audit_sink=context.metadata.get("audit_sink", self.audit_sink), audit_context=audit_context)
        return runtime.run(program.ast, args=dict(context.metadata.get("args", {})), bindings=bindings, source=getattr(program, "source", None), run_id=context.run_id)

    def _execute(self, operation, context, handle):
        if handle.status == "cancelled": return
        if context.expired():
            handle.fail(TimeoutError("execution deadline expired")); return
        try:
            from .infrastructure.operations import RegisteredCallable
            if isinstance(operation, RegisteredCallable):
                result = operation()
            else:
                disk = self._disk()
                result = self._script(operation, context, disk) if isinstance(operation, str) or hasattr(operation, "ast") else self._call(operation, context, disk) if callable(operation) else (_ for _ in ()).throw(TypeError("unsupported execution operation"))
            handle.complete(result)
        except BaseException as exc: handle.fail(exc)

    def _queue_state(self):
        if self.run_state is None and self.queue is not None:
            self.run_state = RunStateStore(self.queue.store)
        return self.run_state

    def enqueue_operation(self, operation, context: Optional[ExecutionContext] = None,
                          *, idempotency_key=None, task_id=None):
        """Persist one operation without executing it."""
        if self.queue is None:
            raise RuntimeError("queued execution is not configured")
        context = context or ExecutionContext()
        key = idempotency_key if idempotency_key is not None else context.metadata.get("idempotency_key")
        operation_id = str(context.metadata.get("operation_id") or uuid.uuid4().hex)
        context.metadata["operation_id"] = operation_id
        if self.operations is not None:
            from .infrastructure.operations import describe_operation, UnserializableOperation
            try:
                described = describe_operation(operation)
                if described["kind"] == "callable":
                    described["payload"]["args"] = list(context.metadata.get("args", ()) or ())
                    described["payload"]["kwargs"] = dict(context.metadata.get("kwargs", {}) or {})
                self.operations.save(operation_id, described["kind"], described["payload"])
            except UnserializableOperation:
                pass
        task = self.queue.enqueue({"operation_id": operation_id, "run_id": context.run_id}, idempotency_key=key, task_id=task_id, operation_id=operation_id)
        context.metadata.setdefault("task_id", task.id)
        context.metadata.setdefault("idempotency_key", key)
        context.metadata.setdefault("attempt", 0)
        context.metadata.setdefault("queue_id", getattr(self.queue, "namespace", None))
        self._queued_operations.setdefault(task.id, operation)
        self._queued_contexts.setdefault(task.id, context)
        self._queue_state().create(context.run_id, idempotency_key=key)
        return task

    def run_next(self, *, lease_seconds=None, now=None):
        """Claim and execute exactly one task synchronously."""
        if self.queue is None:
            raise RuntimeError("queued execution is not configured")
        task = self.queue.claim(lease_seconds=lease_seconds, now=now)
        if task is None:
            return None
        context = self._queued_contexts.get(task.id)
        operation = self._queued_operations.get(task.id)
        if operation is None and self.operations is not None:
            op_id = (task.payload or {}).get("operation_id") if isinstance(task.payload, dict) else None
            if op_id and self.operations.has(op_id):
                from .infrastructure.operations import OperationError
                try:
                    operation = self.operations.recover(op_id)
                except OperationError:
                    operation = None
            if context is None and op_id:
                from .contracts import ExecutionContext
                context = ExecutionContext(run_id=(task.payload or {}).get("run_id") or task.id,
                                           metadata={"operation_id": op_id, "task_id": task.id, "attempt": task.attempt})
                context.metadata.setdefault("idempotency_key", task.idempotency_key)
        state = self._queue_state()
        run_id = context.run_id if context is not None else task.id
        if context is not None:
            context.metadata["attempt"] = task.attempt
            context.metadata.setdefault("task_id", task.id)
            context.metadata.setdefault("queue_id", getattr(self.queue, "namespace", None))
            context.metadata.setdefault("operation_id", task.operation_id)
        handle = self._queued_handles.get(task.id) or RunHandle(run_id)
        self._queued_handles[task.id] = handle
        record = state.create(run_id) if state is not None else None
        if record is not None and record.status == "pending":
            state.transition(run_id, "running", expected_version=record.version)
        if context is None or operation is None:
            error = RuntimeError("queued operation is not registered in this process")
            handle.fail(error)
        else:
            self._execute(operation, context, handle)
        if handle.status == "succeeded":
            self.queue.complete(task.id, handle.result, lease_id=task.lease_id)
            if state is not None and state.get(run_id).status == "running": state.transition(run_id, "succeeded", result_ref=handle.result)
        elif handle.status == "failed":
            queued = self.queue.fail(task.id, repr(handle.error), retry=True, lease_id=task.lease_id)
            if state is not None and state.get(run_id).status == "running":
                if queued.status == "queued": state.transition(run_id, "pending")
                else: state.transition(run_id, "failed", error_ref=repr(handle.error))
        else:
            self.queue.cancel(task.id)
            if state is not None and state.get(run_id).status == "running": state.transition(run_id, "cancelled")
        return handle

    def poll_once(self, **kwargs):
        """Run one queued task; no background thread is started."""
        return self.run_next(**kwargs)

    def submit(self, operation, context: Optional[ExecutionContext] = None):
        context = context or ExecutionContext()
        disk = self._disk()
        state = self.run_state
        if state is None and disk is not None:
            state = self.run_state = RunStateStore.from_data_disk(disk)
        if state is not None:
            record = state.create(context.run_id, idempotency_key=context.metadata.get("idempotency_key"))
            if record.status in state.TERMINAL:
                handle = RunHandle(record.run_id, status=record.status, result=record.result_ref)
                if record.status == "succeeded": handle.complete(record.result_ref)
                elif record.status == "failed": handle.fail(RuntimeError(record.error_ref or "execution failed"))
                else: handle.cancel()
                return handle
            if record.status == "running": raise RuntimeError(f"run {record.run_id} is already running; concurrent submit is not allowed")
            state.transition(record.run_id, "running", expected_version=record.version)
        handle = RunHandle(context.run_id)
        self._execute(operation, context, handle)
        if state is not None:
            if handle.status == "succeeded": state.transition(handle.run_id, "succeeded", result_ref=handle.result)
            elif handle.status == "failed": state.transition(handle.run_id, "failed", error_ref=repr(handle.error))
            elif handle.status == "cancelled": state.transition(handle.run_id, "cancelled")
        return handle

    def run(self, operation, context: Optional[ExecutionContext] = None):
        return self.submit(operation, context).wait()

    def cancel(self, handle):
        return handle.cancel()

ExecutionPlaneAdapter = ExecutionService
__all__ = ["ExecutionService", "ExecutionPlaneAdapter"]
