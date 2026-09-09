import json
import tempfile
import unittest
from pathlib import Path

from pyvdisk.infrastructure.checkpoint import CheckpointStore
from pyvdisk.vscript.checkpoint import CheckpointStore as LegacyCheckpointStore


class FakeVFS:
    def __init__(self):
        self.files = {}
    def exists(self, path):
        return path in self.files
    def read_file(self, path):
        return self.files[path]
    def write_file(self, path, data):
        self.files[path] = data


class CheckpointStoreTests(unittest.TestCase):
    def test_vscript_import_is_canonical_alias(self):
        self.assertIs(LegacyCheckpointStore, CheckpointStore)

    def test_vfs_backend_and_legacy_vfs_constructor(self):
        vfs = FakeVFS()
        store = CheckpointStore(vfs, "/state.json")
        store.mark_success("job", 7)
        self.assertEqual(json.loads(vfs.files["/state.json"]), {"job": {"last_event": "7", "status": "success"}})
        migrated = LegacyCheckpointStore(vfs, "/state.json")
        self.assertEqual(migrated.last_event("job"), "7")

    def test_explicit_host_backend_is_atomic_and_persistent(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "nested" / "checkpoints.json"
            store = CheckpointStore(backend="host", path=path)
            store.set("job", {"value": "迁移"})
            self.assertEqual(CheckpointStore(backend="host", path=path).get("job"), {"value": "迁移"})
            self.assertEqual(list(path.parent.glob(".*")), [])

    def test_legacy_host_path_constructor(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoints.json"
            store = LegacyCheckpointStore(path)
            store.mark_success("old", "event-1")
            self.assertEqual(CheckpointStore(backend="host", path=path).last_event("old"), "event-1")

    def test_backend_must_be_explicit_when_no_target(self):
        with self.assertRaises(TypeError):
            CheckpointStore()


if __name__ == "__main__":
    unittest.main()
