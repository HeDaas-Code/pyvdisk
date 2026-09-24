"""Windows compatibility layer (``pyvdisk.compat``).

CI runs on Linux, so the Windows branches would otherwise never execute. Two
things make them testable from here: ``compat.describe()`` says which
implementation is live, and ``compat.use_implementation("windows")`` plus a
stand-in for ``msvcrt`` runs the emulation against real files.

That is not a substitute for a Windows runner -- the stand-in's lock is
in-process, so it cannot show that two *processes* contend -- but it does
execute the emulation, including the contention and timeout paths, which is
where the interesting logic is.

The last test is the regression guard for the whole exercise: nothing outside
``compat`` may reach for ``fcntl``, ``msvcrt``, ``os.pread`` or ``os.pwrite``
directly, because that is how the Windows gap opened in the first place.
"""
from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import pytest

from pyvdisk import DataDisk, VFS, compat

ROOT = Path(__file__).resolve().parents[1]


class FakeMsvcrt:
    """In-process stand-in for the Windows locking API.

    ``msvcrt.locking`` locks a byte range of an open file.  Keying the held
    ranges by ``(st_dev, st_ino)`` reproduces the part the emulation depends on:
    a second lock on the same file fails until the first is released.
    """

    LK_NBLCK, LK_UNLCK = 2, 0

    def __init__(self):
        self.held = {}

    def locking(self, fd, mode, nbytes):
        stat = os.fstat(fd)
        key = (stat.st_dev, stat.st_ino)
        if mode == self.LK_UNLCK:
            self.held.pop(key, None)
            return
        if key in self.held:
            raise OSError(13, "already locked")
        self.held[key] = nbytes


@pytest.fixture
def windows_emulation(monkeypatch):
    """Force the emulated implementation, with a stand-in for msvcrt."""
    fake = FakeMsvcrt()
    monkeypatch.setattr(compat, "_msvcrt", fake)
    with compat.use_implementation("windows"):
        yield fake


def _lock_file(tmp_path, name="lock"):
    path = tmp_path / name
    return os.open(str(path), os.O_CREAT | os.O_RDWR)


# ---- the live platform ----------------------------------------------------

def test_describe_reports_the_live_implementation():
    info = compat.describe()
    assert info["implementation"] in ("posix", "windows")
    assert info["implementation"] == ("posix" if os.name == "posix" else "windows")
    assert set(info) >= {"platform", "positional_io", "locking", "directory_fsync", "uid_gid", "symlinks"}
    if os.name == "posix":
        assert info["locking"] == "fcntl.flock"
        assert info["positional_io"] == "os.pread/os.pwrite"
        assert info["directory_fsync"] is True


def test_uid_and_gid_are_integers():
    assert isinstance(compat.uid(), int)
    assert isinstance(compat.gid(), int)
    if os.name == "posix":
        assert compat.uid() == os.getuid()
        assert compat.gid() == os.getgid()
    else:
        assert (compat.uid(), compat.gid()) == (0, 0)


def test_can_symlink_agrees_with_the_platform(tmp_path):
    supported = compat.can_symlink(str(tmp_path))
    assert isinstance(supported, bool)
    if os.name == "posix":
        assert supported is True
    assert not list(tmp_path.iterdir()), "the probe must clean up after itself"


# ---- positional IO -------------------------------------------------------

def test_positional_io_reads_and_writes_at_an_offset(tmp_path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"0" * 64)
    fd = os.open(str(path), os.O_RDWR)
    try:
        assert compat.pwrite(fd, b"HELLO", 10) == 5
        assert compat.pread(fd, 5, 10) == b"HELLO"
        # Reads are positioned: the cursor is irrelevant and nothing else moved.
        assert compat.pread(fd, 3, 0) == b"000"
        assert path.read_bytes()[10:15] == b"HELLO"
    finally:
        os.close(fd)


def test_positional_read_returns_short_only_at_end_of_file(tmp_path):
    path = tmp_path / "short.bin"
    path.write_bytes(b"abc")
    fd = os.open(str(path), os.O_RDONLY)
    try:
        assert compat.pread(fd, 10, 0) == b"abc"
        assert compat.pread(fd, 10, 3) == b""
    finally:
        os.close(fd)


def test_the_disk_helpers_pad_a_short_read(tmp_path):
    """``_pread_all`` pads to the requested length; that path uses compat.pread."""
    from pyvdisk.disk import _pread_all, _pwrite_all

    path = tmp_path / "block.bin"
    with open(path, "w+b", buffering=0) as handle:
        _pwrite_all(handle, 4, b"ABCD")
        assert handle.seek(0, os.SEEK_END) == 8
        assert _pread_all(handle, 0, 8) == b"\x00\x00\x00\x00ABCD"


# ---- locking -------------------------------------------------------------

def test_locking_is_exclusive_between_handles(tmp_path):
    first, second = _lock_file(tmp_path), _lock_file(tmp_path)
    try:
        assert compat.lock(first) is True
        assert compat.lock(second, blocking=False) is False
        compat.unlock(first)
        assert compat.lock(second, blocking=False) is True
    finally:
        compat.unlock(first)
        compat.unlock(second)
        os.close(first)
        os.close(second)


def test_lock_timeout_gives_up_instead_of_waiting_forever(tmp_path):
    first, second = _lock_file(tmp_path), _lock_file(tmp_path)
    try:
        assert compat.lock(first) is True
        started = time.monotonic()
        assert compat.lock(second, timeout=0.05) is False
        waited = time.monotonic() - started
        assert 0.04 <= waited < 5.0, f"timeout waited {waited:.3f}s"
    finally:
        compat.unlock(first)
        compat.unlock(second)
        os.close(first)
        os.close(second)


def test_unlock_on_a_closed_handle_is_not_an_error(tmp_path):
    fd = _lock_file(tmp_path)
    os.close(fd)
    compat.unlock(fd)  # must not raise: close() runs on every teardown path


def test_fsync_dir_flushes_a_real_directory(tmp_path):
    if os.name != "posix":
        pytest.skip("directory fsync is a POSIX facility")
    assert compat.fsync_dir(str(tmp_path)) is True
    assert compat.fsync_dir(str(tmp_path / "missing")) is False


# ---- the emulated implementation -----------------------------------------

def test_emulated_positional_io_matches_the_native_one(tmp_path, windows_emulation):
    path = tmp_path / "emulated.bin"
    path.write_bytes(bytes(range(64)))
    fd = os.open(str(path), os.O_RDWR)
    try:
        assert compat.pwrite(fd, b"XY", 8) == 2
        assert compat.pread(fd, 4, 7) == bytes([7, 88, 89, 10])
        assert compat.pread(fd, 4, 61) == bytes([61, 62, 63])
    finally:
        os.close(fd)


def test_emulated_locking_contends_and_times_out(tmp_path, windows_emulation):
    first, second = _lock_file(tmp_path), _lock_file(tmp_path)
    try:
        assert compat.lock(first) is True
        assert compat.lock(second, blocking=False) is False
        assert compat.lock(second, timeout=0.05) is False
        compat.unlock(first)
        assert compat.lock(second, blocking=False) is True
    finally:
        compat.unlock(first)
        compat.unlock(second)
        os.close(first)
        os.close(second)


def test_a_disk_round_trips_under_the_windows_emulation(tmp_path, windows_emulation):
    """The emulated positional IO and locking must carry real disk workloads."""
    plain = tmp_path / "plain.vdisk"
    VFS.create(str(plain), 8 << 20)
    with VFS(str(plain)) as vfs:
        vfs.makedirs("/deep/nested")
        vfs.write_file("/deep/nested/small.txt", b"windows path")
        assert vfs.read_file("/deep/nested/small.txt") == b"windows path"
        # Big enough to span many blocks, so pwrite is exercised repeatedly.
        payload = bytes(range(256)) * 4096
        vfs.write_file("/big.bin", payload)
        assert vfs.read_file("/big.bin") == payload

    container = tmp_path / "container.vdisk"
    DataDisk.create(str(container), 16 << 20)
    with DataDisk(str(container)) as disk:
        disk.fs.write_file("/state.json", b'{"step": 1}')
        with disk.transaction():
            disk.fs.write_file("/state.json", b'{"step": 2}')
        assert disk.fs.read_file("/state.json") == b'{"step": 2}'
        disk.checkpoints.set("cursor", {"page": 7})
        disk.checkpoints.save()
        assert disk.checkpoints.get("cursor") == {"page": 7}


def test_the_two_implementations_agree_on_a_whole_workload(tmp_path, windows_emulation):
    """Same operations, same bytes: only the primitives underneath differ."""
    def run(directory):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "agree.vdisk"
        VFS.create(str(path), 4 << 20)
        with VFS(str(path)) as vfs:
            vfs.write_file("/a.txt", b"payload")
            vfs.write_file("/b.txt", b"x" * 5000)
            return [vfs.read_file("/a.txt"), vfs.read_file("/b.txt"), sorted(vfs.listdir("/"))]

    # The fixture forced the emulation; nest the native one back in for the A/B.
    with compat.use_implementation("posix"):
        native = run(tmp_path / "native")
    emulated = run(tmp_path / "emulated")
    assert native == emulated


# ---- the regression guard ------------------------------------------------

#: Reaching for these directly is what made the package POSIX-only.
FORBIDDEN = (
    (re.compile(r"^\s*import\s+fcntl\b|^\s*from\s+fcntl\s+import\b"), "imports fcntl directly"),
    (re.compile(r"^\s*import\s+msvcrt\b|^\s*from\s+msvcrt\s+import\b"), "imports msvcrt directly"),
    (re.compile(r"\bos\.pread\s*\("), "calls os.pread (POSIX only)"),
    (re.compile(r"\bos\.pwrite\s*\("), "calls os.pwrite (POSIX only)"),
    (re.compile(r"\bos\.getuid\s*\(|\bos\.getgid\s*\("), "calls os.getuid/getgid (POSIX only)"),
)


def test_only_compat_reaches_for_platform_primitives():
    offenders = []
    for path in sorted((ROOT / "pyvdisk").rglob("*.py")):
        if path.name == "compat.py":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            for pattern, why in FORBIDDEN:
                if pattern.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number} {why}")
    assert not offenders, "route these through pyvdisk.compat:\n" + "\n".join(offenders)


def test_host_writes_flush_the_directory_through_compat():
    """host.py used to fsync a directory fd, which Windows cannot open at all."""
    source = (ROOT / "pyvdisk" / "vscript" / "host.py").read_text(encoding="utf-8")
    assert "compat.fsync_dir(" in source
    assert not re.search(r"os\.fsync\s*\(\s*dirfd", source)
