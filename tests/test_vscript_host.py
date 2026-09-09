import os
import tempfile
import unittest
from pathlib import Path
from pyvdisk.vscript.host import HostCapability
from pyvdisk.vscript.errors import CapabilityError

class HostCapabilityTests(unittest.TestCase):
    def test_allowlist_and_policy(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"in").write_bytes(b"ok")
            p=HostCapability([root], [root]).proxy()
            self.assertEqual(p.read(root/"in"), b"ok")
            p.write(root/"out", b"new")
            self.assertEqual((root/"out").read_bytes(), b"new")
    def test_symlink_escape_and_special_files_rejected(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            root=Path(td); (root/"link").symlink_to(outside, target_is_directory=True)
            (Path(outside)/"secret").write_bytes(b"secret")
            p=HostCapability([root], [root]).proxy()
            with self.assertRaises(CapabilityError): p.read(root/"link"/"secret")
            with self.assertRaises(CapabilityError): p.write(root/"link"/"new", b"x")
            if hasattr(os, "mkfifo"):
                os.mkfifo(root/"pipe")
                with self.assertRaises(CapabilityError): p.read(root/"pipe")
    def test_read_and_write_roots_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); read=root/"read"; write=root/"write"; read.mkdir(); write.mkdir()
            p=HostCapability([read], [write]).proxy()
            (read/"x").write_bytes(b"x")
            self.assertEqual(p.read(read/"x"), b"x")
            with self.assertRaises(CapabilityError): p.write(read/"bad", b"x")
            with self.assertRaises(CapabilityError): p.read(write/"missing")

if __name__ == "__main__": unittest.main()
