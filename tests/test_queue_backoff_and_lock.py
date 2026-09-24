"""Issue #1 B5/B9: queue backoff + cross-process lock."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pyvdisk.infrastructure import CheckpointStore, DurableQueue


class BackoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_backoff_defers_claim_after_fail(self):
        clock = {"t": 0.0}
        def fake_now():
            return clock["t"]
        store = CheckpointStore.from_host(self.root / "q")
        q = DurableQueue(store, backoff_base=10.0, backoff_max=60.0, clock=fake_now)
        t = q.enqueue({"k": 1})
        claimed = q.claim(now=0)
        q.fail(t.id, "boom", retry=True, lease_id=claimed.lease_id)
        # backoff is active → not claimable immediately
        self.assertIsNone(q.claim(now=1))
        # after the backoff window expires it becomes claimable
        clock["t"] = 30.0
        got = q.claim(now=30.0)
        self.assertIsNotNone(got)
        self.assertEqual(got.attempt, 2)

    def test_backoff_none_disables_stamping(self):
        store = CheckpointStore.from_host(self.root / "q2")
        q = DurableQueue(store, backoff_base=None)
        t = q.enqueue({"k": 1})
        claimed = q.claim(now=0)
        q.fail(t.id, "boom", retry=True, lease_id=claimed.lease_id)
        self.assertIsNotNone(q.claim(now=1))

    def test_retry_clears_deadline(self):
        store = CheckpointStore.from_host(self.root / "q3")
        q = DurableQueue(store, backoff_base=10.0)
        t = q.enqueue({"k": 1})
        claimed = q.claim(now=0)
        q.fail(t.id, "boom", retry=False, lease_id=claimed.lease_id)
        ret = q.retry(t.id)
        self.assertEqual(ret.status, "queued")
        got = q.claim(now=1)
        self.assertIsNotNone(got)


class LockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_flock_sidecar_created_for_host(self):
        store = CheckpointStore.from_host(self.root / "ck")
        with store.locked():
            self.assertTrue((self.root / "ck.lock").exists())
        # lock released after exit

    def test_locked_is_reentrant_per_thread(self):
        store = CheckpointStore.from_host(self.root / "ck2")
        with store.locked():
            with store.locked():  # nested reentrant acquisition must not deadlock
                store.set("a", 1)
        self.assertEqual(store.get("a"), 1)

    def test_two_processes_serialize_writes(self):
        # Spawn a child that acquires the lock and holds it; the parent must
        # block until released. Verifies cross-process mutual exclusion.
        lock_path = str(self.root / "cclock")
        repo_root = str(Path(__file__).resolve().parents[1])
        child = """
import sys, time
sys.path.insert(0, %r)
from pyvdisk.infrastructure import CheckpointStore
s = CheckpointStore.from_host(%r + '.json')
with s.locked():
    print('locked')
    sys.stdout.flush()
    time.sleep(0.8)
""" % (repo_root, lock_path)
        script = self.root / "child.py"
        script.write_text(child)
        proc = subprocess.Popen([sys.executable, str(script)], stdout=subprocess.PIPE, text=True)
        import time
        line = proc.stdout.readline().strip()
        self.assertEqual(line, "locked")
        store = CheckpointStore.from_host(self.root / "cclock.json")
        start = time.time()
        with store.locked():
            elapsed = time.time() - start
        # Parent acquisition is serialized after the child releases
        proc.wait(timeout=5)
        self.assertGreaterEqual(elapsed, 0.5)


if __name__ == "__main__":
    unittest.main()
