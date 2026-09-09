import tempfile
import unittest
from pathlib import Path

from pyvdisk import DurableQueue
from pyvdisk.infrastructure import CheckpointStore, InvalidTaskState


class DurableQueueTests(unittest.TestCase):
    def make_queue(self, path, **kwargs):
        return DurableQueue(CheckpointStore(backend="host", path=path), **kwargs)

    def test_idempotent_persistence_and_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"
            queue = self.make_queue(path)
            first = queue.enqueue({"value": 1}, idempotency_key="same")
            self.assertEqual(queue.enqueue({"value": 2}, idempotency_key="same").id, first.id)
            claimed = queue.claim(now=100)
            self.assertEqual(claimed.attempt, 1)
            done = queue.complete(claimed.id, {"ok": True}, lease_id=claimed.lease_id)
            self.assertEqual(done.status, "succeeded")
            reopened = self.make_queue(path)
            self.assertEqual(reopened.get(first.id).result, {"ok": True})

    def test_retry_and_dead_letter_after_attempt_limit(self):
        with tempfile.TemporaryDirectory() as td:
            queue = self.make_queue(Path(td) / "queue.json", max_attempts=2, lease_seconds=5)
            task = queue.enqueue("work")
            claimed = queue.claim(now=0)
            self.assertEqual(queue.fail(task.id, "temporary", retry=True).status, "queued")
            claimed = queue.claim(now=1)
            failed = queue.fail(task.id, "permanent", retry=True, lease_id=claimed.lease_id)
            self.assertEqual((failed.status, failed.dead_letter), ("failed", True))

    def test_recover_stale_requeues_or_dead_letters(self):
        with tempfile.TemporaryDirectory() as td:
            queue = self.make_queue(Path(td) / "queue.json", max_attempts=1, lease_seconds=5)
            task = queue.enqueue("work")
            claimed = queue.claim(now=0)
            recovered = queue.recover_stale(now=6)
            self.assertEqual(recovered[0].id, task.id)
            self.assertTrue(queue.get(task.id).dead_letter)

    def test_cancel_and_lease_validation(self):
        with tempfile.TemporaryDirectory() as td:
            queue = self.make_queue(Path(td) / "queue.json")
            task = queue.enqueue("work")
            self.assertEqual(queue.cancel(task.id).status, "cancelled")
            with self.assertRaises(InvalidTaskState):
                queue.complete(task.id)


if __name__ == "__main__":
    unittest.main()
