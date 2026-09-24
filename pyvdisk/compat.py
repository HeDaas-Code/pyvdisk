"""Platform compatibility layer: the one place the OS primitives live.

Everything in pyvdisk that is not plain buffered file IO is funnelled through
this module:

======================  ==========================  ==============================
primitive               POSIX                       Windows
======================  ==========================  ==============================
whole-file lock         ``fcntl.flock(LOCK_EX)``    ``msvcrt.locking`` byte range
positional read         ``os.pread``                ``os.lseek`` + ``os.read``
positional write        ``os.pwrite``               ``os.lseek`` + ``os.write``
directory fsync         ``os.fsync`` on the dir fd  no-op (no directory handles)
uid / gid               ``os.getuid/getgid``        ``0``
======================  ==========================  ==============================

Why a lock on the emulated positional IO: ``os.pread``/``os.pwrite`` are
atomic, ``lseek`` + ``read`` is not.  Two threads sharing one handle could
interleave and read the wrong block, so the emulation serialises through a
module-level lock.  That costs throughput on Windows only, and only while a
block IO is in flight; it is not a global lock over the whole disk.

The Windows byte-range lock covers ``[0, LOCK_BYTES)`` -- the same "whole file"
scope ``flock`` gives us, because every handle in this package locks from
offset 0.  It is advisory in the same sense ``flock`` is: both processes have
to cooperate by calling this module.

No third-party imports, and importing this module never fails: ``describe()``
reports which implementation is live, which is what the tests and the
``pyvdisk doctor`` style diagnostics read.
"""

from __future__ import annotations

import contextlib
import os
import sys
import threading
import time

try:  # POSIX
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - platform dependent
    _fcntl = None

try:  # Windows
    import msvcrt as _msvcrt
except ImportError:
    _msvcrt = None

IS_WINDOWS = sys.platform.startswith("win")
IS_POSIX = os.name == "posix"

#: Byte range the Windows emulation locks: every caller locks from offset 0, so
#: a single wide range is equivalent to ``flock``'s whole-file scope.
LOCK_BYTES = 0x7FFFFFFF

#: How long ``lock()`` waits between attempts when it cannot block in the kernel.
POLL_SECONDS = 0.01

#: Positional IO is emulated with a shared lock unless the OS provides real
#: ``pread``/``pwrite``.
_HAS_POSITIONAL = hasattr(os, "pread") and hasattr(os, "pwrite")

_POSITIONAL_LOCK = threading.RLock()

# Test seams: the emulation is exercised on POSIX by forcing it and injecting a
# stand-in for ``msvcrt``.  Production code never touches these.
_FORCED: str | None = None


def implementation() -> str:
    """Return the live implementation name: ``"posix"`` or ``"windows"``."""
    if _FORCED is not None:
        return _FORCED
    return "posix" if (_HAS_POSITIONAL and _fcntl is not None) else "windows"


@contextlib.contextmanager
def use_implementation(name: str):
    """Force an implementation for the duration of the block (tests only)."""
    global _FORCED
    previous, _FORCED = _FORCED, name
    try:
        yield
    finally:
        _FORCED = previous


def describe() -> dict:
    """What this platform gives us, for diagnostics and test assertions."""
    return {
        "platform": sys.platform,
        "implementation": implementation(),
        "positional_io": "os.pread/os.pwrite" if _HAS_POSITIONAL else "lseek+read/write",
        "locking": "fcntl.flock" if _fcntl is not None else ("msvcrt.locking" if _msvcrt is not None else "none"),
        "directory_fsync": IS_POSIX,
        "uid_gid": hasattr(os, "getuid") and hasattr(os, "getgid"),
        "symlinks": hasattr(os, "symlink"),
    }


# ---- positional IO -------------------------------------------------------

def pread(fd: int, length: int, offset: int) -> bytes:
    """Read up to ``length`` bytes at ``offset`` without moving the file cursor.

    Returns fewer bytes only at end of file, like ``os.pread``.
    """
    if _HAS_POSITIONAL and implementation() == "posix":
        return os.pread(fd, length, offset)
    with _POSITIONAL_LOCK:
        os.lseek(fd, offset, os.SEEK_SET)
        return os.read(fd, length)


def pwrite(fd: int, data: bytes, offset: int) -> int:
    """Write ``data`` at ``offset`` without moving the file cursor.

    Returns the number of bytes written, like ``os.pwrite``.
    """
    if _HAS_POSITIONAL and implementation() == "posix":
        return os.pwrite(fd, data, offset)
    with _POSITIONAL_LOCK:
        os.lseek(fd, offset, os.SEEK_SET)
        return os.write(fd, data)


# ---- whole-file locking --------------------------------------------------

def _retry(attempt, *, blocking: bool, timeout: float | None) -> bool:
    """Poll ``attempt`` until it succeeds, the timeout expires, or once if non-blocking.

    ``LK_LOCK`` gives up after about ten seconds on Windows, so the emulation
    never uses it: it polls ``LK_NBLCK`` instead and keeps the wait semantics
    ``flock`` has (wait forever by default, or for ``timeout`` seconds).
    """
    if blocking and timeout is None:
        while True:
            try:
                attempt()
                return True
            except OSError:
                time.sleep(POLL_SECONDS)
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        try:
            attempt()
            return True
        except OSError:
            if not blocking:
                return False
            if deadline is not None and time.monotonic() >= deadline:
                return False
            time.sleep(POLL_SECONDS)


def _windows_locking(fd: int, *, blocking: bool, timeout: float | None) -> bool:
    if _msvcrt is None:
        raise OSError("no locking primitive available on this platform")

    def attempt():
        os.lseek(fd, 0, os.SEEK_SET)
        _msvcrt.locking(fd, _msvcrt.LK_NBLCK, LOCK_BYTES)

    return _retry(attempt, blocking=blocking, timeout=timeout)


def lock(fd: int, *, blocking: bool = True, timeout: float | None = None) -> bool:
    """Take an exclusive whole-file lock.

    Returns True when the lock is held.  With ``blocking=False`` a contended
    lock returns False instead of waiting; with a ``timeout`` it gives up after
    that many seconds.  Raises OSError only when the platform offers no locking
    primitive at all.
    """
    if implementation() == "posix" and _fcntl is not None:
        if blocking and timeout is None:
            _fcntl.flock(fd, _fcntl.LOCK_EX)
            return True

        def attempt():
            _fcntl.flock(fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)

        return _retry(attempt, blocking=blocking, timeout=timeout)
    return _windows_locking(fd, blocking=blocking, timeout=timeout)


def unlock(fd: int) -> None:
    """Release a lock taken by :func:`lock`.  Never raises on a stale handle."""
    try:
        if implementation() == "posix" and _fcntl is not None:
            _fcntl.flock(fd, _fcntl.LOCK_UN)
        elif _msvcrt is not None:
            os.lseek(fd, 0, os.SEEK_SET)
            _msvcrt.locking(fd, _msvcrt.LK_UNLCK, LOCK_BYTES)
    except OSError:
        # Losing the lock because the descriptor is gone is not an error worth
        # raising: close() is on every teardown path, including failure paths.
        pass


# ---- durability ----------------------------------------------------------

def fsync_dir(path: str) -> bool:
    """Flush a directory entry so a rename inside it survives a crash.

    Returns True when the platform actually flushed something.  Windows cannot
    open a directory as a file and has no directory-fsync, so this is a no-op
    there and returns False -- NTFS journals the rename itself.
    """
    if not IS_POSIX or not hasattr(os, "O_DIRECTORY"):
        return False
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError:
        return False
    try:
        os.fsync(fd)
        return True
    except OSError:
        return False
    finally:
        with contextlib.suppress(OSError):
            os.close(fd)


# ---- identity ------------------------------------------------------------

def uid() -> int:
    """Effective uid, or 0 where the platform has no such notion."""
    getter = getattr(os, "getuid", None)
    return int(getter()) if getter is not None else 0


def gid() -> int:
    """Effective gid, or 0 where the platform has no such notion."""
    getter = getattr(os, "getgid", None)
    return int(getter()) if getter is not None else 0


def uid_or(default: int) -> int:
    """Effective uid, or ``default`` where the platform has no such notion.

    Prefer this over ``uid() or default``: uid 0 is root, not "unset".
    """
    getter = getattr(os, "getuid", None)
    return int(getter()) if getter is not None else int(default)


def gid_or(default: int) -> int:
    """Effective gid, or ``default`` where the platform has no such notion."""
    getter = getattr(os, "getgid", None)
    return int(getter()) if getter is not None else int(default)


def can_symlink(directory: str) -> bool:
    """Whether a real symlink can be created in ``directory`` right now.

    Windows only allows this with developer mode or elevation, so callers that
    want to exercise symlink paths have to ask rather than assume.
    """
    if not hasattr(os, "symlink"):
        return False
    target = os.path.join(directory, ".pyvdisk-symlink-probe")
    link = target + ".lnk"
    try:
        with contextlib.suppress(OSError):
            os.unlink(link)
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        return False
    finally:
        with contextlib.suppress(OSError):
            os.unlink(link)
    return True


__all__ = [
    "IS_WINDOWS", "IS_POSIX", "LOCK_BYTES",
    "implementation", "use_implementation", "describe",
    "pread", "pwrite", "lock", "unlock", "fsync_dir",
    "uid", "gid", "uid_or", "gid_or", "can_symlink",
]
