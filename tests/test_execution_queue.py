import tempfile
import unittest
from pathlib import Path

from pyvdisk import ExecutionContext, ExecutionService, DurableQueue
from pyvdisk.infrastructure import CheckpointStore


class QueuedExecutionTests(unittest.TestCase):
    def make_service(self, path, **kwargs):
        store = CheckpointStore(backend="host", path=path)
        return ExecutionService(queue=DurableQueue(store, **kwargs))

    def test_enqueue_then_poll_associates_run_state(self):
        with tempfile.TemporaryDirectory() as td:
            service = self.make_service(Path(td) / "queue.json")
            context = ExecutionContext(run_id="queued-1")
            task = service.enqueue_operation(lambda ctx: ctx.run_id, context)
            self.assertEqual(task.status, "queued")
            self.assertEqual(service.poll_once().wait(), "queued-1")
            self.assertEqual(service.queue.get(task.id).status, "succeeded")
            self.assertEqual(service.run_state.get("queued-1").status, "succeeded")

    def test_failure_requeues_and_then_dead_letters(self):
        with tempfile.TemporaryDirectory() as td:
            service = self.make_service(Path(td) / "queue.json", max_attempts=2)
            context = ExecutionContext(run_id="retry-1")
            task = service.enqueue_operation(lambda: (_ for _ in ()).throw(ValueError("bad")), context)
            first = service.run_next()
            self.assertEqual(first.status, "failed")
            self.assertEqual(service.queue.get(task.id).status, "queued")
            self.assertEqual(service.run_next().status, "failed")
            final = service.queue.get(task.id)
            self.assertEqual((final.status, final.dead_letter), ("failed", True))
            self.assertEqual(service.run_state.get("retry-1").status, "failed")

    def test_claim_lease_is_explicit_and_poll_is_not_background(self):
        with tempfile.TemporaryDirectory() as td:
            service = self.make_service(Path(td) / "queue.json", lease_seconds=5)
            task = service.enqueue_operation(lambda: 1)
            claimed = service.queue.claim(now=10)
            self.assertEqual(claimed.id, task.id)
            self.assertEqual(claimed.status, "running")
            self.assertIsNone(service.poll_once(now=10))
            service.queue.recover_stale(now=16)
            self.assertEqual(service.poll_once(now=16).wait(), 1)


if __name__ == "__main__":
    unittest.main()
