import threading

import pytest

from pyvdisk import ExecutionContext, ExecutionService, DurableQueue
from pyvdisk.infrastructure import CheckpointStore


@pytest.mark.parametrize("raises", [False, True])
def test_running_cancel_is_not_overwritten(tmp_path, raises):
    service = ExecutionService(queue=DurableQueue(CheckpointStore(backend="host", path=tmp_path / "queue.json")))
    entered, release = threading.Event(), threading.Event()

    def operation():
        entered.set()
        assert release.wait(5)
        if raises:
            raise ValueError("late failure")
        return "late success"

    handle = service.enqueue_async(operation, ExecutionContext(run_id="cancel-test"))
    task = service.queue.list()[0]
    service.start_workers()
    try:
        assert entered.wait(5)
        assert handle.cancel()
    finally:
        release.set()
        service.stop_workers(timeout=5)
    assert service.worker_count == 0
    assert handle.status == "cancelled"
    assert handle.error is None
    assert service.queue.get(task.id).status == "cancelled"
    assert service.run_state.get(handle.run_id).status == "cancelled"
