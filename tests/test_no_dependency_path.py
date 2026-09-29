"""The zero-dependency promise: no hnswlib, no fusepy, no build step.

Two things make the promise real, and both are tested here:

* ``pyproject.toml`` declares no runtime dependencies, so ``pip install pyvdisk``
  never tries to compile hnswlib;
* ``VectorDisk`` falls back to the built-in flat index, so a collection still
  answers exactly when the accelerator is absent -- and a collection written by
  either backend can be read by the other.

``examples/quickstart.py`` is the user-visible half of the same claim, so it runs
here in a subprocess with ``hnswlib`` blocked: if it ever starts needing the
accelerator, this test fails rather than the user's first five minutes.
"""
from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from pyvdisk import VectorDisk, vector_index
from pyvdisk.vector_index import FlatIndex, FlatIndexError

ROOT = Path(__file__).resolve().parents[1]
QUICKSTART = ROOT / "examples" / "quickstart.py"

try:  # the accelerator may legitimately be absent
    import hnswlib  # noqa: F401
    HAVE_HNSWLIB = True
except ImportError:  # pragma: no cover - depends on the environment
    HAVE_HNSWLIB = False

needs_hnswlib = pytest.mark.skipif(not HAVE_HNSWLIB, reason="hnswlib is not installed here")


class _BlockHnswlib:
    """Context manager that makes ``import hnswlib`` fail for the block."""

    def __enter__(self):
        import builtins

        self._real = builtins.__import__

        def blocked(name, *args, **kwargs):
            if name == "hnswlib":
                raise ImportError("hnswlib blocked for this test")
            return self._real(name, *args, **kwargs)

        builtins.__import__ = blocked
        return self

    def __exit__(self, *exc):
        import builtins

        builtins.__import__ = self._real


def _collection(disk):
    disk.create_collection("docs", 3, metric="cosine")
    disk.upsert_many("docs", [
        {"id": "a", "vector": [1.0, 0.0, 0.0], "metadata": {"kind": "news"}},
        {"id": "b", "vector": [0.0, 1.0, 0.0], "metadata": {"kind": "blog"}},
        {"id": "c", "vector": [0.9, 0.1, 0.0], "metadata": {"kind": "news"}},
    ])
    return disk


def _ids(hits):
    return [hit["id"] for hit in hits]


# ---- the packaging promise ------------------------------------------------

def test_declared_runtime_dependencies_are_empty():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^dependencies\s*=\s*\[(?P<body>.*?)\]", text, re.M | re.S)
    assert match, "pyproject.toml has no [project] dependencies field"
    assert match.group("body").strip() == "", (
        "the core must stay stdlib-only; extras belong in [project.optional-dependencies]"
    )
    extras = text.split("[project.optional-dependencies]", 1)[1]
    assert "hnswlib" in extras and "fusepy" in extras, "the accelerators must remain installable"


def test_the_quickstart_example_exists_and_is_standard_library_only():
    source = QUICKSTART.read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")) and "pyvdisk" not in stripped:
            module = stripped.split()[1].split(".")[0]
            assert module in {
                "__future__", "importlib", "os", "sys", "tempfile", "pathlib", "json",
                "time", "hashlib", "shutil", "argparse",
            }, f"quickstart must not need {module}"


# ---- the flat index -------------------------------------------------------

def test_read_kind_identifies_the_writer():
    index = FlatIndex("cosine", 3)
    assert vector_index.read_kind(vector_index.serialize(index)) == vector_index.KIND_FLAT
    assert vector_index.read_kind(b"\x00\x01hnswlib-bytes") == vector_index.KIND_HNSW


def test_flat_index_round_trips_through_its_serialised_form():
    index = FlatIndex("l2", 2)
    index.add_items([[0.0, 1.0], [2.0, 2.0]], [7, 9])
    restored = vector_index.deserialize(vector_index.serialize(index))
    assert restored.space == "l2" and restored.dim == 2
    assert restored.labels == [7, 9]
    labels, distances = restored.knn_query([[0.0, 1.0]], k=1)
    assert labels == [[7]] and distances == [[0.0]]


def test_a_truncated_flat_index_is_rejected_rather_than_misread():
    index = FlatIndex("cosine", 3)
    index.add_item(1, [1.0, 0.0, 0.0])
    payload = vector_index.serialize(index)
    with pytest.raises(FlatIndexError):
        vector_index.deserialize(payload[:-2])
    with pytest.raises(FlatIndexError):
        vector_index.deserialize(b"not-a-flat-index")


def test_flat_index_rejects_an_unknown_metric_and_a_wrong_dimension():
    with pytest.raises(FlatIndexError):
        FlatIndex("hamming", 3)
    index = FlatIndex("cosine", 3)
    with pytest.raises(FlatIndexError):
        index.add_item(1, [1.0, 0.0])


def test_flat_index_distances_match_hnswlib_conventions():
    """cosine -> 1 - similarity, l2 -> squared euclidean, ip -> 1 - dot."""
    cosine = FlatIndex("cosine", 2)
    cosine.add_items([[1.0, 0.0], [0.0, 1.0]], [1, 2])
    _, distances = cosine.knn_query([[1.0, 0.0]], k=2)
    assert distances[0] == [0.0, 1.0]
    l2 = FlatIndex("l2", 2)
    l2.add_item(1, [0.0, 0.0])
    _, distances = l2.knn_query([[3.0, 4.0]], k=1)
    assert distances[0] == [25.0]
    ip = FlatIndex("ip", 2)
    ip.add_item(1, [2.0, 0.0])
    _, distances = ip.knn_query([[3.0, 0.0]], k=1)
    assert distances[0] == [-5.0]


# ---- the vector disk without the accelerator ------------------------------

def test_the_vector_disk_works_without_hnswlib(tmp_path):
    path = str(tmp_path / "vectors.vdisk")
    VectorDisk.create(path, 16 << 20)
    with _BlockHnswlib():
        with VectorDisk(path) as disk:
            _collection(disk)
            assert disk.count("docs") == 3
            hits = disk.search("docs", [1.0, 0.0, 0.0], k=3)
            assert _ids(hits) == ["a", "c", "b"]
            assert hits[0]["distance"] == pytest.approx(0.0, abs=1e-6)
            assert _ids(disk.search("docs", [1.0, 0.0, 0.0], k=3, where={"kind": "news"})) == ["a", "c"]
            assert disk.get("docs", "a")["metadata"] == {"kind": "news"}
            assert disk.delete("docs", "b") is True
            assert disk.count("docs") == 2
            assert vector_index.read_kind(disk.vfs.read_file(disk._dir("docs") + "/index.hnsw")) == "flat"
        # Reopen with the accelerator still blocked: the flat index persists.
        with VectorDisk(path) as disk:
            assert disk.count("docs") == 2
            assert _ids(disk.search("docs", [1.0, 0.0, 0.0], k=2)) == ["a", "c"]


def test_writes_work_without_hnswlib_after_a_rebuild(tmp_path):
    """Upserts and deletes rebuild the index; that path must not need hnswlib either."""
    path = str(tmp_path / "mutate.vdisk")
    VectorDisk.create(path, 16 << 20)
    with _BlockHnswlib():
        with VectorDisk(path) as disk:
            disk.create_collection("docs", 2)
            disk.upsert("docs", "a", [1.0, 0.0])
            disk.upsert("docs", "b", [0.0, 1.0])
            disk.upsert("docs", "a", [0.5, 0.5])  # replace
            assert disk.count("docs") == 2
            assert disk.delete("docs", "b") is True
            assert _ids(disk.search("docs", [1.0, 0.0], k=5)) == ["a"]


@needs_hnswlib
def test_both_backends_agree_on_the_same_collection(tmp_path):
    flat_path, hnsw_path = str(tmp_path / "flat.vdisk"), str(tmp_path / "hnsw.vdisk")
    for path in (flat_path, hnsw_path):
        VectorDisk.create(path, 16 << 20)
    with _BlockHnswlib():
        with VectorDisk(flat_path) as disk:
            _collection(disk)
            flat = [(hit["id"], round(hit["distance"], 6)) for hit in disk.search("docs", [1.0, 0.0, 0.0], k=3)]
    with VectorDisk(hnsw_path) as disk:
        _collection(disk)
        hnsw = [(hit["id"], round(hit["distance"], 6)) for hit in disk.search("docs", [1.0, 0.0, 0.0], k=3)]
    assert flat == hnsw


@needs_hnswlib
def test_an_hnsw_written_collection_is_readable_without_hnswlib(tmp_path):
    path = str(tmp_path / "mixed.vdisk")
    VectorDisk.create(path, 16 << 20)
    with VectorDisk(path) as disk:
        _collection(disk)
        assert vector_index.read_kind(disk.vfs.read_file(disk._dir("docs") + "/index.hnsw")) == "hnsw"
    with _BlockHnswlib():
        with VectorDisk(path) as disk:
            # Correct results, linear time: better than refusing to open the disk.
            assert _ids(disk.search("docs", [1.0, 0.0, 0.0], k=3)) == ["a", "c", "b"]


@needs_hnswlib
def test_a_flat_written_collection_is_readable_with_hnswlib(tmp_path):
    path = str(tmp_path / "flat-then-hnsw.vdisk")
    VectorDisk.create(path, 16 << 20)
    with _BlockHnswlib():
        with VectorDisk(path) as disk:
            _collection(disk)
    with VectorDisk(path) as disk:
        assert _ids(disk.search("docs", [1.0, 0.0, 0.0], k=3)) == ["a", "c", "b"]


# ---- the example the user actually runs -----------------------------------

def _run_quickstart(workdir: Path, block_hnswlib: bool) -> subprocess.CompletedProcess:
    runner = workdir / ("blocked.py" if block_hnswlib else "plain.py")
    runner.write_text(textwrap.dedent(f"""
        import builtins, runpy, sys
        if {block_hnswlib!r}:
            real = builtins.__import__
            def blocked(name, *args, **kwargs):
                if name == "hnswlib":
                    raise ImportError("hnswlib blocked for this test")
                return real(name, *args, **kwargs)
            builtins.__import__ = blocked
        sys.argv = ["quickstart.py", {str(workdir / 'out')!r}]
        runpy.run_path({str(QUICKSTART)!r}, run_name="__main__")
    """), encoding="utf-8")
    return subprocess.run([sys.executable, str(runner)], capture_output=True, text=True,
                          cwd=str(ROOT), timeout=300)


def test_the_quickstart_example_runs_without_optional_dependencies(tmp_path):
    result = _run_quickstart(tmp_path, block_hnswlib=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "built-in flat (no dependency)" in result.stdout
    assert "chain ok = True" in result.stdout
    assert "may not escape" in result.stdout, "the refusal demo must still run"


def test_the_quickstart_example_also_runs_with_the_accelerator(tmp_path):
    if not HAVE_HNSWLIB:
        pytest.skip("hnswlib is not installed here")
    result = _run_quickstart(tmp_path, block_hnswlib=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "index backend: hnswlib" in result.stdout
