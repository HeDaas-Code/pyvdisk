"""Issue #1 C3/C4: running-conflict detection and capability-scoped disk view."""
from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from pyvdisk.execution import ExecutionContext, ExecutionService
from pyvdisk.infrastructure import DataDisk, ScopedDataDisk
from pyvdisk.infrastructure.checkpoint import CheckpointStore
from pyvdisk.infrastructure.run_state import RunStateStore


class SubmitConflictTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_repeated_submit_with_running_run_id_raises(self):
        from pyvdisk.contracts import CapabilityGrant, Capability
        ctx = ExecutionContext(run_id="run-conflict")
        DataDisk.create(self.root / "disk.vdisk", 4 * 1024 * 1024)
        disk = DataDisk(self.root / "disk.vdisk")
        service = ExecutionService(disk)
        started = threading.Event()
        release = threading.Event()

        def slow(ctx_arg, view):
            started.set()
            release.wait(timeout=5)
            return "ok"

        t = threading.Thread(target=lambda: service.submit(slow, ctx))
        t.start()
        try:
            started.wait(timeout=2)
            with self.assertRaises(RuntimeError) as cm:
                service.submit(slow, ctx)
            self.assertIn("already running", str(cm.exception))
        finally:
            release.set()
            t.join(timeout=3)

    def test_scoped_view_is_passed_to_callable(self):
        DataDisk.create(self.root / "disk2.vdisk", 4 * 1024 * 1024)
        disk = DataDisk(self.root / "disk2.vdisk")
        service = ExecutionService(disk)
        seen = {}

        def probe(ctx_arg, view):
            seen["view"] = view
            return view.__class__.__name__

        handle = service.submit(probe, ExecutionContext(run_id="run-scope"))
        self.assertEqual(handle.status, "succeeded")
        self.assertIsInstance(seen.get("view"), ScopedDataDisk)
        self.assertEqual(handle.result, "ScopedDataDisk")

    def test_scoped_view_rejects_protected_internals(self):
        DataDisk.create(self.root / "disk3.vdisk", 4 * 1024 * 1024)
        disk = DataDisk(self.root / "disk3.vdisk")
        service = ExecutionService(disk)

        def probe(ctx_arg, view):
            view.fs.write_file("/.system/wal.jsonl", b"data")

        ctx = ExecutionContext(run_id="run-protect")
        handle = service.submit(probe, ctx)
        self.assertEqual(handle.status, "failed")
        self.assertIsInstance(handle.error, PermissionError)


class CheckpointBytesTests(unittest.TestCase):
    def test_bytes_round_trip_through_host_backend(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore.from_host(Path(td) / "ck.json")
            payload = b"\x00\x01\x02\x03\xff\xfe\xfd"
            store.set("raw", payload)
            reloaded = CheckpointStore.from_host(Path(td) / "ck.json")
            self.assertEqual(reloaded.get("raw"), payload)

    def test_bytes_nested_in_dict(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore.from_host(Path(td) / "ck2.json")
            store.set("doc", {"a": 1, "blob": b"hello\x00world"})
            reloaded = CheckpointStore.from_host(Path(td) / "ck2.json")
            self.assertEqual(reloaded.get("doc"), {"a": 1, "blob": b"hello\x00world"})


if __name__ == "__main__":
    unittest.main()
