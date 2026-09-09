from pyvdisk import ExecutionContext, ExecutionService, DurableQueue
from pyvdisk.infrastructure import CheckpointStore

def test_idempotent_enqueue_executes_one_successful_internal_operation(tmp_path):
    service = ExecutionService(queue=DurableQueue(CheckpointStore(backend="host", path=tmp_path / "q.json")))
    calls=[]
    def operation():
        calls.append(1)
        return {"ok": True}
    context=ExecutionContext(run_id="once-run")
    first=service.enqueue_operation(operation, context, idempotency_key="once-key")
    second=service.enqueue_operation(operation, context, idempotency_key="once-key")
    assert second.id == first.id
    assert service.run_next().wait() == {"ok": True}
    assert service.run_next() is None
    assert calls == [1]
    assert service.queue.get(first.id).result == {"ok": True}
