"""虚拟磁盘镜像的块级读写。

一个 VirtualDisk 就是一个普通文件，按固定大小的"块"组织。
本模块只负责字节数据的读写，不关心文件系统语义。
"""

from __future__ import annotations

import os
import warnings
import contextlib
from typing import Optional

try:  # POSIX advisory locking; Windows remains a safe no-op fallback.
    import fcntl
except ImportError:  # pragma: no cover - platform dependent
    fcntl = None

DEFAULT_BLOCK_SIZE = 4096


def _pread_all(f, offset: int, length: int) -> bytes:
    """从文件 f 的 offset 处读取 length 字节，保证读满（EOF 除外）。

    使用 os.pread：原子定位读取，不依赖文件游标，且绕过 Python 缓冲。
    """
    fd = f.fileno()
    chunks = []
    remaining = length
    cur = offset
    while remaining > 0:
        n = os.pread(fd, remaining, cur)
        if not n:
            break  # EOF
        chunks.append(n)
        cur += len(n)
        remaining -= len(n)
    data = b"".join(chunks)
    if len(data) < length:
        data = data + b"\x00" * (length - len(data))
    return data


def _pwrite_all(f, offset: int, data: bytes) -> None:
    """向文件 f 的 offset 处写入 data，保证写满。

    使用 os.pwrite：原子定位写入，绕过 Python 缓冲，跨句柄立即可见。
    """
    fd = f.fileno()
    view = memoryview(data)
    cur = offset
    written = 0
    total = len(data)
    while written < total:
        n = os.pwrite(fd, view[written:], cur)
        cur += n
        written += n


class VirtualDisk:
    """虚拟磁盘镜像：把一个普通文件当成块设备来读写。

    不需要任何管理员权限——它只是一个普通文件的读写。
    """

    def __init__(self, path: str, block_size: int = DEFAULT_BLOCK_SIZE, *, legacy: bool = False):
        if legacy:
            warnings.warn(
                "VirtualDisk is a low-level legacy entry point; prefer VFS or DataDisk.",
                DeprecationWarning, stacklevel=2,
            )
        self.path = path
        self.block_size = block_size
        self.nblocks: int = 0
        self._f = None
        self._locked = False

    # ---- 生命周期 ----
    def create(self, size_bytes: int) -> int:
        """创建一个指定大小的空磁盘镜像文件。

        返回块数。已存在的文件会被截断覆盖。
        """
        if size_bytes <= 0:
            raise ValueError("磁盘大小必须为正数")
        nblocks = size_bytes // self.block_size
        if nblocks < 16:
            raise ValueError(
                f"磁盘太小，至少需要 {16 * self.block_size} 字节（16 个块）"
            )
        # 用 truncate 一次性分配稀疏文件
        with open(self.path, "wb") as f:
            f.truncate(nblocks * self.block_size)
            f.flush()
            os.fsync(f.fileno())
        self.nblocks = nblocks
        return nblocks

    def open(self, mode: str = "r+b") -> "VirtualDisk":
        if self._f is not None:
            return self
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"磁盘镜像不存在: {self.path}")
        # buffering=0：无缓冲二进制 IO，每次读写直达 OS。
        # 这样多个文件句柄（多线程各自 open 同一镜像）能通过 OS 页缓存
        # 立即看到彼此的写入，避免陈旧读。
        self._f = open(self.path, mode, buffering=0)
        if fcntl is not None and any(c in mode for c in "wa+"):
            try:
                # Blocking acquisition serializes writers across threads/processes.
                # Non-blocking failure caused ordinary concurrent VFS operations to
                # fail spuriously instead of waiting for the image lock.
                fcntl.flock(self._f.fileno(), fcntl.LOCK_EX)
                self._locked = True
            except OSError:
                self._f.close(); self._f = None
                raise RuntimeError(f"磁盘无法获取写锁: {self.path}")
        self.nblocks = os.stat(self.path).st_size // self.block_size
        return self

    def close(self) -> None:
        if self._f is not None:
            self._f.flush()
            if self._locked and fcntl is not None:
                fcntl.flock(self._f.fileno(), fcntl.LOCK_UN)
            self._f.close()
            self._f = None
            self._locked = False

    def flush(self) -> None:
        if self._f is not None:
            self._f.flush()
            os.fsync(self._f.fileno())

    def __enter__(self):
        if self._f is None:
            self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    # ---- 块级 IO（使用 os.pread/os.pwrite 定位读写，原子且跨句柄一致）----
    def read_block(self, block_no: int) -> bytes:
        if self._f is None:
            raise RuntimeError("磁盘未打开")
        if block_no < 0 or block_no >= self.nblocks:
            raise ValueError(f"块号越界: {block_no} (总块数 {self.nblocks})")
        offset = block_no * self.block_size
        return _pread_all(self._f, offset, self.block_size)

    def write_block(self, block_no: int, data: bytes) -> None:
        if self._f is None:
            raise RuntimeError("磁盘未打开")
        if block_no < 0 or block_no >= self.nblocks:
            raise ValueError(f"块号越界: {block_no} (总块数 {self.nblocks})")
        if len(data) > self.block_size:
            raise ValueError(
                f"数据长度 {len(data)} 超过块大小 {self.block_size}"
            )
        if len(data) < self.block_size:
            data = data + b"\x00" * (self.block_size - len(data))
        _pwrite_all(self._f, block_no * self.block_size, data)

    def read_bytes(self, offset: int, length: int) -> bytes:
        """按字节偏移读取（用于读取 inode 表等）。"""
        if self._f is None:
            raise RuntimeError("磁盘未打开")
        return _pread_all(self._f, offset, length)

    def write_bytes(self, offset: int, data: bytes) -> None:
        if self._f is None:
            raise RuntimeError("磁盘未打开")
        _pwrite_all(self._f, offset, data)

    def truncate_bytes(self, size_bytes: int) -> int:
        """按字节调整磁盘容量（只能扩大到 block_size 整数倍）。

        返回变更后的总块数。
        """
        if self._f is None:
            raise RuntimeError("磁盘未打开")
        if size_bytes < 0:
            raise ValueError("大小不能为负")
        new_nblocks = size_bytes // self.block_size
        self._f.truncate(new_nblocks * self.block_size)
        self.nblocks = new_nblocks
        return new_nblocks
