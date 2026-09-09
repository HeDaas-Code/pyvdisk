import tempfile
from pathlib import Path
from pyvdisk import ExecutionContext, ExecutionService, DurableQueue
from pyvdisk.infrastructure import CheckpointStore, RunStateStore


def test_operation_id_and_result_survive_duplicate_enqueue():
    with tempfile.TemporaryDirectory() as td:
        q = DurableQueue(CheckpointStore(backend="host", path=Path(td) / "q.json"))
        service = ExecutionService(queue=q)
        calls = []
        ctx = ExecutionContext(run_id="run-1", metadata={"idempotency_key": "idem-1"})
        first = service.enqueue_operation(lambda: calls.append(1) or {"ok": True}, ctx)
        duplicate = service.enqueue_operation(lambda: calls.append(2) or {"ok": False}, ExecutionContext(run_id="run-2"), idempotency_key="idem-1")
        assert duplicate.id == first.id
        assert duplicate.operation_id == first.operation_id
        assert service.run_next().wait() == {"ok": True}
        assert calls == [1]
        stored = q.get(first.id)
        assert stored.status == "succeeded"
        assert stored.result == {"ok": True}
        assert stored.operation_id == first.operation_id


def test_inline_retry_by_run_id_returns_persisted_result():
    with tempfile.TemporaryDirectory() as td:
        q = DurableQueue(CheckpointStore(backend="host", path=Path(td) / "q.json"))
        service = ExecutionService(run_state=RunStateStore(q.store))
        calls = []
        ctx = ExecutionContext(run_id="run-2", metadata={"idempotency_key": "idem-2"})
        operation = lambda: calls.append(1) or 42
        assert service.run(operation, ctx) == 42
        assert service.run(operation, ExecutionContext(run_id="run-2", metadata={"idempotency_key": "idem-2"})) == 42
        assert calls == [1]
