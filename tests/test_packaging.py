"""A6/E: packaging metadata smoke tests (Issue #1 A6).

These guard the promises ``pyproject.toml`` makes, because CI installs the package
exactly the way it declares: ``pip install -e .[dev]`` on every version listed in
``requires-python``.
"""
import ast
import re
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted(list((ROOT / "pyvdisk").rglob("*.py")) + list((ROOT / "tests").rglob("*.py")))


def _pyproject_text():
    return (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def _readme_text():
    return (ROOT / "README.md").read_text(encoding="utf-8")


def _same_quote_nesting(source):
    """Yield the line numbers of f-strings that reuse their own quote inside a field.

    PEP 701 (3.12) allows ``f"{d["k"]}"``; older parsers end the string at the inner
    quote and fail with ``f-string: unmatched '['``. ``ast.parse(feature_version=...)``
    does not cover that rewrite, so the replacement fields are inspected directly: a
    field may not contain the delimiter of the literal it sits in.

    Only the fields are inspected, not the whole literal, because a JoinedStr spanning
    implicitly concatenated literals reports all of them as one source segment.

    Replacement-field positions are only reliable from 3.12 on (older ASTs report the
    whole literal), so this is called there only. That is not a gap: on 3.9-3.11 a
    PEP 701 construct makes ``import pyvdisk`` raise SyntaxError, so test collection
    fails outright and there is nothing left for a detector to add.
    """
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.JoinedStr):
            continue
        segment = ast.get_source_segment(source, node)
        if not segment:
            continue
        body = re.sub(r"^[rbufRBUF]*", "", segment)
        marker = body[:1]
        if marker not in ('"', "'"):
            continue
        for value in node.values:
            if not isinstance(value, ast.FormattedValue):
                continue
            field = ast.get_source_segment(source, value) or ""
            if re.search(r"(?<!\\)" + marker, field):
                yield node.lineno
                break


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

    def test_sdist_carries_the_license_and_the_changelog(self):
        """E asked for both files; a distribution that omits them is not compliant."""
        names = self._sdist_names()
        top = set()
        for name in names:
            parts = name.split("/", 1)
            if len(parts) == 2 and "/" not in parts[1]:   # files directly under pyvdisk-<version>/
                top.add(parts[1])
        self.assertIn("LICENSE", top, top)
        self.assertIn("CHANGELOG.md", top, f"MANIFEST.in 没把变更日志带进 sdist: {top}")

    def test_readme_badge_matches_the_declared_python_floor(self):
        """The badge claimed 3.12+ while the metadata claimed 3.9+."""
        floor = re.search(r'requires-python\s*=\s*">=\s*(\d+\.\d+)"', _pyproject_text())
        self.assertIsNotNone(floor, "pyproject.toml 缺少 requires-python")
        badge = re.search(r"badge/Python-(\d+\.\d+)%2B", _readme_text())
        self.assertIsNotNone(badge, "README 缺少 Python 版本徽章")
        self.assertEqual(badge.group(1), floor.group(1), "README 徽章与 requires-python 不一致")

    def test_dev_extra_declares_what_the_suite_imports(self):
        """CI sets the suite up with ``pip install -e .[dev]``, so dev must be complete.

        This module imports ``setuptools.build_meta``, and an editable install builds in
        an isolated environment -- setuptools is simply not in the test environment
        unless the extra asks for it (that is exactly how CI failed on 3.12).
        """
        match = re.search(r"^dev\s*=\s*\[(?P<items>.*?)\]", _pyproject_text(), re.S | re.M)
        self.assertIsNotNone(match, "pyproject.toml 缺少 dev extra")
        self.assertIn("setuptools", match.group("items"), "dev extra 必须声明 setuptools")

    def test_sources_parse_on_the_declared_python_floor(self):
        """``requires-python`` is a promise, and CI's oldest matrix job enforces it."""
        match = re.search(r'requires-python\s*=\s*">=\s*(?P<major>\d+)\.(?P<minor>\d+)"', _pyproject_text())
        self.assertIsNotNone(match, "pyproject.toml 缺少 requires-python")
        version = (int(match.group("major")), int(match.group("minor")))
        offenders = []
        for source in SOURCES:
            body = source.read_text(encoding="utf-8")
            ast.parse(body, filename=str(source), feature_version=version)
            if sys.version_info >= (3, 12):
                offenders += [(str(source.relative_to(ROOT)), line) for line in _same_quote_nesting(body)]
        self.assertEqual(offenders, [], f"这些 f-string 需要比 {version[0]}.{version[1]} 更新的 Python: {offenders}")


if __name__ == "__main__":
    unittest.main()
