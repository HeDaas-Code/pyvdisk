"""Issue #1 A5: host checkpoint save is atomic (tmp+rename), no partial JSON."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pyvdisk.infrastructure import CheckpointStore


class AtomicVfsSaveTests(unittest.TestCase):
    def test_save_is_atomic_and_readable(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "ck.json"
            store = CheckpointStore.from_host(target)
            store.set("k", {"a": [1, 2, 3], "b": b"x00x01"})
            # no stray tmp files left behind
            self.assertEqual(list(Path(td).glob(".ck.json.*")), [])
            reloaded = CheckpointStore.from_host(target)
            self.assertEqual(reloaded.get("k")["a"], [1, 2, 3])

    def test_load_invalid_json_raises(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "bad.json"
            target.write_text("{not valid json")
            with self.assertRaises(ValueError):
                CheckpointStore.from_host(target)


if __name__ == "__main__":
    unittest.main()
