"""Issue #1 D: the FUSE bridge had no tests.

A real mount needs ``/dev/fuse``, so CI can never exercise one. Everything between
the kernel and the VFS can still be tested: the operations object is a plain class
that needs only a handful of names from ``fuse``, and a stub module supplies them.
"""
from __future__ import annotations

import errno
import os
import stat as stat_module
import sys
import threading
import types
import unittest.mock as mock
from pathlib import Path

import pytest

from pyvdisk import VFS
from pyvdisk.fs import FSError
from pyvdisk.fuse_mount import (
    _build_fuse_class,
    _have_fuse,
    _VFuseOperations,
    mount,
    mount_in_thread,
)


class _FuseOSError(OSError):
    def __init__(self, errno_):
        self.errno = errno_
        super().__init__(errno_, os.strerror(errno_))


class _StubFuse(types.ModuleType):
    """The names pyvdisk imports from fusepy, and a FUSE() that records the call."""

    ENOENT = errno.ENOENT
    EINVAL = errno.EINVAL
    FuseOSError = _FuseOSError

    class Operations:
        pass

    class LoggingMixIn:
        pass

    def __init__(self, name="fuse"):
        super().__init__(name)
        self.calls = []

    def FUSE(self, ops, mountpoint, **kwargs):
        self.calls.append((ops, mountpoint, kwargs))


@pytest.fixture
def fuse_stub():
    stub = _StubFuse()
    with mock.patch.dict(sys.modules, {"fuse": stub}):
        yield stub


@pytest.fixture
def vfs(tmp_path):
    image = str(tmp_path / "disk.vdisk")
    VFS.create(image, 8 * 1024 * 1024)
    with VFS(image) as mounted:
        yield mounted


@pytest.fixture
def ops(fuse_stub, vfs):
    return _VFuseOperations(vfs)


# ------------------------------------------------------------------ availability
def test_mount_without_fusepy_explains_how_to_install_it(tmp_path):
    if _have_fuse():
        pytest.skip("fusepy is installed in this environment")
    with pytest.raises(ImportError) as caught:
        mount(object(), str(tmp_path))
    assert "fusepy" in str(caught.value)


def test_have_fuse_follows_the_module(fuse_stub):
    assert _have_fuse() is True


def test_mount_refuses_a_mountpoint_that_is_not_a_directory(fuse_stub, vfs, tmp_path):
    with pytest.raises(FSError):
        mount(vfs, str(tmp_path / "nope"))
    assert fuse_stub.calls == []


def test_mount_hands_the_operations_to_fuse(fuse_stub, vfs, tmp_path):
    mount(vfs, str(tmp_path))
    assert len(fuse_stub.calls) == 1
    ops_, mountpoint, kwargs = fuse_stub.calls[0]
    assert mountpoint == str(tmp_path)
    assert kwargs["foreground"] is False and kwargs["nothreads"] is True
    assert type(ops_).__name__ == "_VFuse"      # each build makes a fresh class
    assert isinstance(ops_, _StubFuse.Operations)
    assert ops_.vfs is vfs


def test_mount_in_thread_signals_ready(fuse_stub, vfs, tmp_path):
    thread, ready = mount_in_thread(vfs, str(tmp_path))
    thread.join(timeout=5)
    assert ready.is_set() and not thread.is_alive()
    assert fuse_stub.calls[0][0].vfs is vfs


# ------------------------------------------------------------------ attributes
def test_getattr_describes_a_directory(ops):
    info = ops._getattr("/")
    assert info["st_mode"] & stat_module.S_IFDIR
    assert info["st_ino"] == ops.vfs._fs_or_raise().resolve("/")
    assert info["st_nlink"] >= 1


def test_getattr_describes_a_file_and_a_symlink(ops, vfs):
    vfs.write_file("/f.txt", b"1234")
    vfs.symlink("f.txt", "/link")
    regular = ops._getattr("/f.txt")
    assert regular["st_mode"] & stat_module.S_IFREG and regular["st_size"] == 4
    link = ops._getattr("/link")
    assert link["st_mode"] & stat_module.S_IFLNK


def test_getattr_on_a_missing_path_is_enoent(ops):
    with pytest.raises(_FuseOSError) as caught:
        ops._getattr("/missing")
    assert caught.value.errno == errno.ENOENT


def test_readdir_lists_children_and_the_dot_entries(ops, vfs):
    vfs.mkdir("/d")
    vfs.write_file("/d/a.txt", b"a")
    vfs.write_file("/d/b.txt", b"b")
    assert ops._readdir("/", None) == [".", "..", "d"]
    assert ops._readdir("/d", None) == [".", "..", "a.txt", "b.txt"]


def test_readdir_on_a_missing_directory_is_reported_not_raised(ops):
    entries = ops._readdir("/missing", None)
    assert entries == ["." + "_raise"]


# ------------------------------------------------------------------ data path
def test_write_then_read_round_trips(ops, vfs):
    ops._create("/new.txt", 0o644)
    assert vfs.exists("/new.txt")
    ops._write("/new.txt", b"hello", 0, None)
    assert ops._read("/new.txt", 5, 0, None) == b"hello"
    ops._write("/new.txt", b"HELLO", 0, None)
    assert ops._read("/new.txt", 5, 0, None) == b"HELLO"
    assert ops._read("/missing", 5, 0, None) == b""


def test_create_is_idempotent(ops, vfs):
    ops._create("/once.txt", 0o600)
    vfs.write_file("/once.txt", b"kept")
    ops._create("/once.txt", 0o600)
    assert vfs.read_file("/once.txt") == b"kept"


def test_truncate_and_chmod(ops, vfs):
    vfs.write_file("/t.txt", b"0123456789")
    ops._truncate("/t.txt", 4)
    assert vfs.read_file("/t.txt") == b"0123"
    ops._chmod("/t.txt", 0o600)
    assert vfs.stat("/t.txt").mode & 0o777 == 0o600
    assert ops._truncate("/missing", 1) == 0     # absent paths are not an error
    assert ops._chmod("/missing", 0o600) == 0


def test_open_and_release_are_accepted(ops):
    assert ops._open("/anything", os.O_RDONLY) == 0
    assert ops._release("/anything", None) == 0


# ------------------------------------------------------------------ namespace
def test_mkdir_rename_rmdir_and_unlink(ops, vfs):
    assert ops._mkdir("/d", 0o755) == 0
    vfs.write_file("/d/f.txt", b"x")
    assert vfs.isdir("/d")
    assert ops._rename("/d/f.txt", "/d/g.txt") == 0
    assert vfs.exists("/d/g.txt") and not vfs.exists("/d/f.txt")
    assert ops._unlink("/d/g.txt") == 0
    assert ops._rmdir("/d") == 0
    assert not vfs.exists("/d")


def test_symlink_and_readlink(ops, vfs):
    """Regression: readlink followed the link and then failed on its target."""
    vfs.write_file("/target.txt", b"x")
    assert ops._symlink("target.txt", "/link") == 0
    assert vfs.lstat("/link").is_symlink
    assert ops._readlink("/link") == "target.txt"
    assert not vfs.lstat("/target.txt").is_symlink


def test_unlinking_a_symlink_keeps_its_target(ops, vfs):
    vfs.write_file("/target.txt", b"x")
    ops._symlink("target.txt", "/link")
    assert ops._unlink("/link") == 0
    assert not vfs.exists("/link")
    assert vfs.read_file("/target.txt") == b"x"


def test_readlink_on_a_regular_file_is_einval(ops, vfs):
    vfs.write_file("/plain.txt", b"x")
    with pytest.raises(_FuseOSError) as caught:
        ops._readlink("/plain.txt")
    assert caught.value.errno == errno.EINVAL


# ------------------------------------------------------------------ wrapper class
def test_the_wrapper_class_exposes_the_fuse_method_names(fuse_stub, vfs):
    wrapper = _build_fuse_class()
    assert issubclass(wrapper, _StubFuse.Operations)
    assert issubclass(wrapper, _StubFuse.LoggingMixIn)
    instance = wrapper(vfs)
    assert instance.vfs is vfs
    for name in ("getattr", "readdir", "read", "write", "create", "mkdir", "rmdir",
                 "unlink", "rename", "truncate", "symlink", "readlink", "open",
                 "release", "chmod", "statfs"):
        assert callable(getattr(instance, name)), name


def test_the_wrapper_delegates_to_the_operations(fuse_stub, vfs):
    wrapper = _build_fuse_class()(vfs)
    vfs.write_file("/f.txt", b"data")
    assert wrapper.read("/f.txt", 4, 0, None) == b"data"
    assert set(wrapper.readdir("/", None)) == {".", "..", "f.txt"}
    assert wrapper.getattr("/f.txt")["st_size"] == 4
    assert wrapper.statfs("/")["f_bsize"] > 0
    assert wrapper.open("/f.txt", os.O_RDONLY) == 0
    assert wrapper.release("/f.txt", os.O_RDONLY, None) == 0


def test_statfs_reports_blocks_and_inodes(ops):
    sb = ops.vfs._fs_or_raise().sb
    assert ops._getattr("/")["st_dev"] == 0
    wrapper = _build_fuse_class()(ops.vfs)
    info = wrapper.statfs("/")
    assert info["f_bsize"] == sb.block_size
    assert info["f_blocks"] == sb.total_blocks
    assert info["f_files"] == sb.total_inodes
