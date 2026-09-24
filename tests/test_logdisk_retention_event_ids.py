"""Issue #1 C2: enforce_retention must drop event_ids for pruned segments."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyvdisk.log_disk import LogDisk


class RetentionEventIdsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "log.vdisk"
        LogDisk.create(str(self.path), 2 * 1024 * 1024)
        self.disk = LogDisk(str(self.path))
        self.disk.mount()
        self.disk.create_stream("s", segment_events=3, retention_seconds=1, max_events=None)

    def test_event_ids_pruned_with_old_segment(self):
        old = 1_000_000_000_000_000_000
        for i in range(3):
            self.disk.append("s", level="INFO", message=f"old{i}", logger="t", timestamp_ns=old + i)
        for i in range(3):
            self.disk.append("s", level="INFO", message=f"new{i}", logger="t", timestamp_ns=old + 1_000_000_000 + i)
        manifest_path = self.disk._dir("s") + "/manifest.json"
        before_ids = set((self.disk._read(manifest_path).get("event_ids") or {}).keys())
        self.assertEqual(len(before_ids), 6)
        pruned = self.disk.enforce_retention("s", now_ns=old + 1_500_000_000)
        self.assertGreater(pruned, 0)
        after_ids = set((self.disk._read(manifest_path).get("event_ids") or {}).keys())
        self.assertLess(len(after_ids), len(before_ids))
        events_now = self.disk.query("s", limit=20)
        for e in events_now:
            self.assertIn(e.event_id, after_ids)


if __name__ == "__main__":
    unittest.main()
