"""Issue #1 A1: FileNamespace mutations roll back on MetadataTransaction abort."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pyvdisk.infrastructure import DataDisk


class _Disk:
    @staticmethod
    def make(tmp):
        path = Path(tmp) / "d.vdisk"
        DataDisk.create(str(path), 4 * 1024 * 1024)
        return DataDisk(str(path))


class TransactionFsRollbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_in_process_abort_restores_file(self):
        with _Disk.make(self.tmp.name) as disk:
            disk.fs.write_file("/keep.txt", b"original")
            try:
                with disk.transaction() as tx:
                    disk.fs.write_file("/keep.txt", b"changed")
                    disk.fs.write_file("/new.txt", b"fresh")
                    raise RuntimeError("boom")
            except RuntimeError:
                pass
            self.assertEqual(disk.fs.read_file("/keep.txt"), b"original")
            self.assertFalse(disk.fs.exists("/new.txt"))

    def test_commit_keeps_changes(self):
        with _Disk.make(self.tmp.name) as disk:
            disk.fs.write_file("/a.txt", b"1")
            with disk.transaction() as tx:
                disk.fs.write_file("/a.txt", b"2")
                disk.fs.write_file("/b.txt", b"new")
            self.assertEqual(disk.fs.read_file("/a.txt"), b"2")
            self.assertEqual(disk.fs.read_file("/b.txt"), b"new")

    def test_no_transaction_passes_through(self):
        with _Disk.make(self.tmp.name) as disk:
            disk.fs.write_file("/x.txt", b"x")
            self.assertEqual(disk.fs.read_file("/x.txt"), b"x")

    def test_rename_rollback(self):
        with _Disk.make(self.tmp.name) as disk:
            disk.fs.write_file("/src.txt", b"src")
            disk.fs.write_file("/dst.txt", b"dst-before")
            try:
                with disk.transaction():
                    disk.fs.rename("/src.txt", "/dst.txt")
                    raise RuntimeError("nope")
            except RuntimeError:
                pass
            self.assertEqual(disk.fs.read_file("/src.txt"), b"src")
            self.assertEqual(disk.fs.read_file("/dst.txt"), b"dst-before")

    def test_rmtree_rollback_restores_tree(self):
        with _Disk.make(self.tmp.name) as disk:
            disk.fs.makedirs("/d1/d2")
            disk.fs.write_file("/d1/a.txt", b"A")
            disk.fs.write_file("/d1/d2/b.txt", b"B")
            try:
                with disk.transaction():
                    disk.fs.rmtree("/d1")
                    raise RuntimeError("stop")
            except RuntimeError:
                pass
            self.assertTrue(disk.fs.isdir("/d1/d2"))
            self.assertEqual(disk.fs.read_file("/d1/a.txt"), b"A")
            self.assertEqual(disk.fs.read_file("/d1/d2/b.txt"), b"B")

    def test_makedirs_rollback_removes_created_dirs(self):
        with _Disk.make(self.tmp.name) as disk:
            try:
                with disk.transaction():
                    disk.fs.makedirs("/x/y/z")
                    self.assertTrue(disk.fs.isdir("/x/y/z"))
                    raise RuntimeError("abort")
            except RuntimeError:
                pass
            self.assertFalse(disk.fs.exists("/x"))
            self.assertFalse(disk.fs.exists("/x/y"))
            self.assertFalse(disk.fs.exists("/x/y/z"))

    def test_mkdir_rollback_removes_dir(self):
        with _Disk.make(self.tmp.name) as disk:
            try:
                with disk.transaction():
                    disk.fs.mkdir("/only-tx")
                    raise RuntimeError("x")
            except RuntimeError:
                pass
            self.assertFalse(disk.fs.exists("/only-tx"))

    def test_nested_transactions_both_aborting_restores(self):
        with _Disk.make(self.tmp.name) as disk:
            disk.fs.write_file("/n.txt", b"0")
            try:
                with disk.transaction():
                    with disk.transaction():
                        disk.fs.write_file("/n.txt", b"inner")
                        disk.fs.write_file("/nested.txt", b"nest")
                        raise RuntimeError("inner")
            except RuntimeError:
                pass
            self.assertEqual(disk.fs.read_file("/n.txt"), b"0")
            self.assertFalse(disk.fs.exists("/nested.txt"))

    def test_crash_then_reopen_restores(self):
        path = Path(self.tmp.name) / "crash.vdisk"
        DataDisk.create(str(path), 4 * 1024 * 1024)
        d = DataDisk(str(path))
        d.mount()
        d.fs.write_file("/p.txt", b"orig")
        with self.assertRaises(RuntimeError):
            with d.transaction():
                d.fs.write_file("/p.txt", b"crash")
                d.fs.write_file("/leak.txt", b"leak")
                raise RuntimeError("crash")
        self.assertEqual(d.fs.read_file("/p.txt"), b"orig")
        self.assertFalse(d.fs.exists("/leak.txt"))


if __name__ == "__main__":
    unittest.main()
