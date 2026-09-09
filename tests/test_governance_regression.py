import tempfile
import unittest
from pathlib import Path

from pyvdisk import (
    Capability,
    CapabilityGrant,
    DataDisk,
    DataDiskError,
    ExecutionContext,
    ExecutionService,
)
from pyvdisk.infrastructure.checkpoint import CheckpointStore
from pyvdisk.infrastructure.disk import FileNamespace, LogNamespace, VectorNamespace
from pyvdisk.vscript.checkpoint import CheckpointStore as LegacyCheckpointStore
from pyvdisk.vscript.errors import CapabilityError
from pyvdisk.vscript.policy import Capability as VScriptCapability


class DataDiskNamespaceGovernanceTests(unittest.TestCase):
    def make_disk(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "data.vdisk"
        disk = DataDisk.create(str(path), 16 * 1024 * 1024)
        self.addCleanup(lambda: (disk.close(), td.cleanup()))
        return disk

    def test_single_file_container_exposes_all_canonical_namespaces(self):
        disk = self.make_disk().mount()
        self.assertTrue(disk.mounted)
        self.assertEqual(disk.manifest()["type"], "pyvdisk-data")
        self.assertIsInstance(disk.fs, FileNamespace)
        self.assertIs(disk.vector, disk.vectors)
        self.assertIs(disk.log, disk.logs)
        self.assertIs(disk.vector, disk.vector_disk)
        self.assertIs(disk.log, disk.log_disk)
        self.assertEqual(set(disk.manifest()["namespaces"]), {"fs", "vectors", "logs", "checkpoints", "wal"})

    def test_namespace_adapters_have_explicit_types_and_legacy_passthrough(self):
        disk = self.make_disk().mount()
        self.assertIsInstance(disk.vector, VectorNamespace)
        self.assertIsInstance(disk.log, LogNamespace)
        self.assertIsInstance(disk.fs, FileNamespace)
        # Existing VFS APIs remain available through the adapter.
        self.assertIs(disk.fs.vfs, disk.vfs)
        self.assertEqual(disk.fs.listdir("/.system"), disk.vfs.listdir("/.system"))
        with self.assertRaises(TypeError):
            disk.fs.write_file("/x", "not bytes")
        with self.assertRaises(TypeError):
            disk.transaction().set(1, "value")

    def test_all_namespaces_reject_access_before_mount(self):
        disk = self.make_disk()
        with self.assertRaises(DataDiskError):
            disk.manifest()
        with self.assertRaises(DataDiskError):
            disk.get_metadata("missing")
        with self.assertRaises(DataDiskError):
            disk.transaction()
        # Namespace objects are deliberately not published until mount.
        self.assertFalse(hasattr(disk, "fs"))
        with self.assertRaises(Exception):
            disk.vfs.exists("/")


class ExecutionServiceGovernanceTests(unittest.TestCase):
    def make_disk(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "exec.vdisk"
        disk = DataDisk.create(str(path), 16 * 1024 * 1024)
        self.addCleanup(lambda: (disk.close(), td.cleanup()))
        return disk

    def test_callable_receives_context_and_mounted_disk(self):
        disk = self.make_disk()
        context = ExecutionContext(run_id="callable-1")
        result = ExecutionService(disk).run(lambda ctx, d: (ctx.run_id, d.mounted, d.fs is not None), context)
        self.assertEqual(result, ("callable-1", True, True))

    def test_vscript_execution_uses_disk_binding_and_capabilities(self):
        disk = self.make_disk()
        context = ExecutionContext(
            capabilities=(CapabilityGrant("script", frozenset({Capability.READ.value})),),
            metadata={"args": {"value": 7}},
        )
        source = 'language "1.0"; import std.fs as fs; let answer = fs.exists(disk, "/.system/manifest.json"); answer;'
        self.assertTrue(ExecutionService(disk).run(source, context))

    def test_callable_type_boundary_and_compatibility_noarg(self):
        service = ExecutionService()
        self.assertEqual(service.run(lambda: "legacy"), "legacy")
        with self.assertRaises(TypeError):
            service.run(42)


class CheckpointIdentityGovernanceTests(unittest.TestCase):
    def test_legacy_checkpoint_import_is_canonical_identity(self):
        self.assertIs(LegacyCheckpointStore, CheckpointStore)

    def test_checkpoint_backend_boundaries_are_unambiguous(self):
        with self.assertRaises(TypeError):
            CheckpointStore()
        with self.assertRaises(TypeError):
            CheckpointStore(backend="vfs")
        with self.assertRaises(TypeError):
            CheckpointStore(object(), backend_name="host")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            self.assertIsInstance(CheckpointStore.from_host(path), CheckpointStore)


if __name__ == "__main__":
    unittest.main()
