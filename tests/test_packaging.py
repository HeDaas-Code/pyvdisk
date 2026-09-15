"""A6/E: packaging metadata smoke tests (Issue #1 A6)."""
import tarfile
import tempfile
import unittest
from pathlib import Path


class PackagingTests(unittest.TestCase):
    def _sdist_names(self):
        from setuptools import build_meta

        with tempfile.TemporaryDirectory() as td:
            build_meta.build_sdist(td)
            archive = next(Path(td).glob("*.tar.gz"))
            with tarfile.open(archive) as tar:
                return [m.name for m in tar.getmembers()]

    def test_sdist_includes_infrastructure_and_vscript(self):
        names = self._sdist_names()
        self.assertTrue(any(n.endswith("/pyvdisk/infrastructure/disk.py") for n in names), names[:20])
        self.assertTrue(any(n.endswith("/pyvdisk/vscript/runtime.py") for n in names), names[:20])

    def test_py_typed_marker_ships(self):
        self.assertTrue((Path(__file__).resolve().parents[1] / "pyvdisk" / "py.typed").exists())


if __name__ == "__main__":
    unittest.main()
