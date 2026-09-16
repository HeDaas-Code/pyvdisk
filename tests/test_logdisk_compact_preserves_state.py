"""Issue #1 C1: log_disk.compact() must preserve consumers metadata."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyvdisk.log_disk import LogDisk


class CompactPreservesStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "log.vdisk"
        LogDisk.create(str(self.path), 2 * 1024 * 1024)
        self.disk = LogDisk(str(self.path))
        self.disk.mount()
        self.disk.create_stream("s", segment_events=3, retention_seconds=None, max_events=None)

    def test_compact_preserves_consumers(self):
        for i in range(5):
            self.disk.append("s", level="INFO", message=f"m{i}", logger="t")
        self.disk.ack("s", "c1", sequence=0)
        self.disk.ack("s", "c1", sequence=2)
        before = self.disk.cursor("s", "c1")
        n = self.disk.compact("s")
        self.assertEqual(n, 5)
        after = self.disk.cursor("s", "c1")
        self.assertEqual(after, before)

    def test_compact_re_emits_all_events(self):
        for i in range(7):
            self.disk.append("s", level="INFO", message=f"x{i}", logger="t")
        n = self.disk.compact("s")
        self.assertEqual(n, 7)
        events = self.disk.query("s", limit=20)
        self.assertEqual(len(events), 7)
        self.assertEqual({e.message for e in events}, {f"x{i}" for i in range(7)})


if __name__ == "__main__":
    unittest.main()
