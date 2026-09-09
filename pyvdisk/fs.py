"""虚拟磁盘上的简易文件系统。

布局（按块编号）：
    块 0                超级块
    块 inode_bitmap_*   inode 位图
    块 block_bitmap_*   数据块位图
    块 inode_table_*    inode 表
    块 data_start..     数据块

inode 结构（128 字节）：
    type(1) mode(2) nlink(2) uid(4) gid(4) size(8)
    atime(8) mtime(8) ctime(8)
    direct[12](48) single(4) double(4)  共 101 字节，补齐到 128

目录项（32 字节）：inode(4) type(1) name(27)
"""

from __future__ import annotations

import functools
import os
import warnings
import struct
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .disk import VirtualDisk, DEFAULT_BLOCK_SIZE


# ---- 锁装饰器（依赖实例上的 self._lock，即 RWLock） ----
def _read_locked(fn):
    """以读锁包裹方法：多读并发，与写互斥。可重入。"""
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        with self._lock.read():
            return fn(self, *args, **kwargs)
    return wrapper


def _write_locked(fn):
    """以写锁包裹方法：独占写，与所有读写互斥。可重入。"""
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        with self._lock.write():
            return fn(self, *args, **kwargs)
    return wrapper


# ---- 跨实例共享锁注册表 ----
# 同一个磁盘镜像可能被多个 VFS/FS 实例打开（如多线程各自 open），
# 它们必须共享同一把锁才能正确互斥。按"盘的真实路径集合"做 key。
_DISK_LOCKS: Dict = {}
_DISK_LOCKS_GUARD = threading.Lock()


def _disk_lock_key(disk) -> Tuple:
    paths: List[str] = []
    if hasattr(disk, "_paths") and disk._paths:
        paths = [os.path.realpath(p) for p in disk._paths]
    elif hasattr(disk, "disks") and disk.disks:
        paths = [os.path.realpath(getattr(d, "path", "")) for d in disk.disks]
    elif hasattr(disk, "path") and disk.path:
        paths = [os.path.realpath(disk.path)]
    else:
        return ("id", id(disk))
    return tuple(sorted(paths))


def _shared_lock_for(disk):
    from .rwlock import RWLock
    key = _disk_lock_key(disk)
    with _DISK_LOCKS_GUARD:
        lk = _DISK_LOCKS.get(key)
        if lk is None:
            lk = RWLock()
            _DISK_LOCKS[key] = lk
        return lk

# ---- 常量 ----
MAGIC = b"VDK1"
VERSION = 1
INODE_SIZE = 128
DIR_ENTRY_SIZE = 32
ROOT_INO = 1  # inode 0 保留（类似 ext2），避免与目录项的空槽位(ino=0)冲突

# 类型
T_FREE = 0
T_FILE = 1
T_DIR = 2
T_SYMLINK = 3

# ---- 结构格式 ----
SUPERBLOCK_FORMAT = "<4sHIQQIQQQQQQQQQQ"
SUPERBLOCK_SIZE = struct.calcsize(SUPERBLOCK_FORMAT)

INODE_FORMAT = "<BHHIIQQQQ12III"
INODE_PACKED_SIZE = struct.calcsize(INODE_FORMAT)  # 101

DIR_ENTRY_FORMAT = "<IB27s"
DIR_ENTRY_PACKED_SIZE = struct.calcsize(DIR_ENTRY_FORMAT)  # 32

PTRS_PER_BLOCK = DEFAULT_BLOCK_SIZE // 4  # 1024
DIRECT_COUNT = 12
MAX_FILE_BLOCKS = DIRECT_COUNT + PTRS_PER_BLOCK + PTRS_PER_BLOCK * PTRS_PER_BLOCK
MAX_FILE_SIZE = MAX_FILE_BLOCKS * DEFAULT_BLOCK_SIZE


@dataclass
class SuperBlock:
    magic: bytes
    version: int
    block_size: int
    total_blocks: int
    total_inodes: int
    inode_size: int
    inode_bitmap_start: int
    inode_bitmap_blocks: int
    block_bitmap_start: int
    block_bitmap_blocks: int
    inode_table_start: int
    inode_table_blocks: int
    data_start: int
    data_blocks: int
    root_inode: int
    created: int

    def to_bytes(self) -> bytes:
        return struct.pack(
            SUPERBLOCK_FORMAT,
            self.magic,
            self.version,
            self.block_size,
            self.total_blocks,
            self.total_inodes,
            self.inode_size,
            self.inode_bitmap_start,
            self.inode_bitmap_blocks,
            self.block_bitmap_start,
            self.block_bitmap_blocks,
            self.inode_table_start,
            self.inode_table_blocks,
            self.data_start,
            self.data_blocks,
            self.root_inode,
            self.created,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SuperBlock":
        fields = struct.unpack(SUPERBLOCK_FORMAT, data[:SUPERBLOCK_SIZE])
        return cls(*fields)


@dataclass
class Inode:
    type: int
    mode: int
    nlink: int
    uid: int
    gid: int
    size: int
    atime: int
    mtime: int
    ctime: int
    direct: List[int]  # 长度 12
    single: int
    double: int

    def to_bytes(self) -> bytes:
        direct = list(self.direct) + [0] * (DIRECT_COUNT - len(self.direct))
        packed = struct.pack(
            INODE_FORMAT,
            self.type,
            self.mode,
            self.nlink,
            self.uid,
            self.gid,
            self.size,
            self.atime,
            self.mtime,
            self.ctime,
            *direct[:DIRECT_COUNT],
            self.single,
            self.double,
        )
        # 补齐到 INODE_SIZE
        return packed + b"\x00" * (INODE_SIZE - len(packed))

    @classmethod
    def from_bytes(cls, data: bytes) -> "Inode":
        t = struct.unpack(INODE_FORMAT, data[:INODE_PACKED_SIZE])
        return cls(
            type=t[0],
            mode=t[1],
            nlink=t[2],
            uid=t[3],
            gid=t[4],
            size=t[5],
            atime=t[6],
            mtime=t[7],
            ctime=t[8],
            direct=list(t[9:21]),
            single=t[21],
            double=t[22],
        )

    @classmethod
    def empty(cls) -> "Inode":
        now = int(time.time())
        return cls(
            type=T_FREE,
            mode=0o644,
            nlink=0,
            uid=0,
            gid=0,
            size=0,
            atime=now,
            mtime=now,
            ctime=now,
            direct=[0] * DIRECT_COUNT,
            single=0,
            double=0,
        )


@dataclass
class Stat:
    ino: int
    type: int
    mode: int
    nlink: int
    size: int
    uid: int
    gid: int
    atime: int
    mtime: int
    ctime: int

    @property
    def is_dir(self) -> bool:
        return self.type == T_DIR

    @property
    def is_file(self) -> bool:
        return self.type == T_FILE

    @property
    def is_symlink(self) -> bool:
        return self.type == T_SYMLINK


def _encode_name(name: str) -> bytes:
    b = name.encode("utf-8")
    if len(b) > 27:
        raise ValueError(f"名字过长（编码后超过 27 字节）: {name!r}")
    return b


def _decode_name(raw: bytes) -> str:
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")


def _ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


class FSError(Exception):
    pass


class FS:
    """挂载在一个 VirtualDisk 上的文件系统实例。"""

    def __init__(self, disk: VirtualDisk, *, legacy: bool = False):
        if legacy:
            warnings.warn(
                "FS is a low-level legacy entry point; prefer VFS or DataDisk.fs.",
                DeprecationWarning, stacklevel=2,
            )
        self.disk = disk
        self.sb: Optional[SuperBlock] = None
        # 读写锁：保护所有元数据操作，多读单写、写互斥（线程安全）。
        # 同一镜像的多个 FS 实例共享同一把锁，保证多线程互斥。
        self._lock = _shared_lock_for(disk)

    # ---- 挂载 / 格式化 ----
    def mount(self) -> "FS":
        """挂载文件系统。

        兼容 VirtualDisk 和 Volume：块 0 都是文件系统超级块
        （Volume 内部已把成员盘的块 0 留给卷元数据，块 1 映射为逻辑块 0）。
        """
        # 确保磁盘已打开
        if hasattr(self.disk, "_f"):
            if self.disk._f is None:
                self.disk.open()
        elif not getattr(self.disk, "disks", None):
            self.disk.open()
        raw = self.disk.read_block(0)
        self.sb = SuperBlock.from_bytes(raw)
        if self.sb.magic != MAGIC:
            raise FSError("不是合法的 vdisk 文件系统（魔数不匹配）")
        if self.sb.block_size != DEFAULT_BLOCK_SIZE:
            raise FSError(
                f"块大小不匹配: 期望 {DEFAULT_BLOCK_SIZE}, 实际 {self.sb.block_size}"
            )
        return self

    @_write_locked
    def flush_superblock(self) -> None:
        assert self.sb is not None
        # 读-改-写：保留 block 0 末尾的磁盘身份尾标（VDID）
        raw = bytearray(self.disk.read_block(0))
        sb_bytes = self.sb.to_bytes()
        raw[:len(sb_bytes)] = sb_bytes
        self.disk.write_block(0, bytes(raw))

    # ---- 位图 ----
    def _bitmap_get(self, start_block: int, idx: int) -> bool:
        byte_off = idx // 8
        block_no = start_block + byte_off // DEFAULT_BLOCK_SIZE
        in_block = byte_off % DEFAULT_BLOCK_SIZE
        data = self.disk.read_block(block_no)
        return bool(data[in_block] & (1 << (idx % 8)))

    def _bitmap_set(self, start_block: int, idx: int, value: bool) -> None:
        byte_off = idx // 8
        block_no = start_block + byte_off // DEFAULT_BLOCK_SIZE
        in_block = byte_off % DEFAULT_BLOCK_SIZE
        data = bytearray(self.disk.read_block(block_no))
        mask = 1 << (idx % 8)
        if value:
            data[in_block] |= mask
        else:
            data[in_block] &= ~mask
        self.disk.write_block(block_no, bytes(data))

    def _bitmap_alloc(self, start_block: int, total: int, hint: int = 0) -> int:
        """在位图中分配一个空闲项，返回其索引。"""
        idx = hint
        for _ in range(total):
            if idx >= total:
                idx = 0
            if not self._bitmap_get(start_block, idx):
                self._bitmap_set(start_block, idx, True)
                return idx
            idx += 1
        raise FSError("位图已满，没有可分配项")

    # ---- inode 分配 ----
    @_write_locked
    def alloc_inode(self) -> int:
        assert self.sb is not None
        return self._bitmap_alloc(self.sb.inode_bitmap_start, self.sb.total_inodes)

    @_write_locked
    def free_inode(self, ino: int) -> None:
        assert self.sb is not None
        self._bitmap_set(self.sb.inode_bitmap_start, ino, False)

    def _inode_offset(self, ino: int) -> int:
        assert self.sb is not None
        return self.sb.inode_table_start * DEFAULT_BLOCK_SIZE + ino * INODE_SIZE

    @_read_locked
    def read_inode(self, ino: int) -> Inode:
        raw = self.disk.read_bytes(self._inode_offset(ino), INODE_SIZE)
        return Inode.from_bytes(raw)

    @_write_locked
    def write_inode(self, ino: int, inode: Inode) -> None:
        self.disk.write_bytes(self._inode_offset(ino), inode.to_bytes())

    # ---- 数据块分配 ----
    @_write_locked
    def alloc_block(self) -> int:
        assert self.sb is not None
        idx = self._bitmap_alloc(self.sb.block_bitmap_start, self.sb.total_blocks,
                                 hint=self.sb.data_start)
        return idx

    @_write_locked
    def free_block(self, block_no: int) -> None:
        assert self.sb is not None
        self._bitmap_set(self.sb.block_bitmap_start, block_no, False)
        # 清空内容，便于后续
        self.disk.write_block(block_no, b"\x00" * DEFAULT_BLOCK_SIZE)

    # ---- inode 的块指针管理 ----
    def _read_ptr(self, block_no: int, idx: int) -> int:
        data = self.disk.read_block(block_no)
        return struct.unpack_from("<I", data, idx * 4)[0]

    def _write_ptr(self, block_no: int, idx: int, value: int) -> None:
        data = bytearray(self.disk.read_block(block_no))
        struct.pack_into("<I", data, idx * 4, value)
        self.disk.write_block(block_no, bytes(data))

    def _get_block_ptr(self, inode: Inode, logical: int) -> int:
        """返回逻辑块对应的物理块号，0 表示未分配。"""
        if logical < DIRECT_COUNT:
            return inode.direct[logical]
        logical -= DIRECT_COUNT
        if logical < PTRS_PER_BLOCK:
            if inode.single == 0:
                return 0
            return self._read_ptr(inode.single, logical)
        logical -= PTRS_PER_BLOCK
        if logical < PTRS_PER_BLOCK * PTRS_PER_BLOCK:
            if inode.double == 0:
                return 0
            outer = logical // PTRS_PER_BLOCK
            inner = logical % PTRS_PER_BLOCK
            inner_block = self._read_ptr(inode.double, outer)
            if inner_block == 0:
                return 0
            return self._read_ptr(inner_block, inner)
        raise FSError("逻辑块号超出最大文件大小")

    def _ensure_block_ptr(self, ino: int, inode: Inode, logical: int) -> int:
        """确保逻辑块已映射到物理块，必要时分配。返回物理块号。"""
        if logical < DIRECT_COUNT:
            if inode.direct[logical] == 0:
                inode.direct[logical] = self.alloc_block()
                self.write_inode(ino, inode)
            return inode.direct[logical]

        logical -= DIRECT_COUNT
        if logical < PTRS_PER_BLOCK:
            if inode.single == 0:
                inode.single = self.alloc_block()
                self.disk.write_block(inode.single, b"\x00" * DEFAULT_BLOCK_SIZE)
                self.write_inode(ino, inode)
            ptr = self._read_ptr(inode.single, logical)
            if ptr == 0:
                ptr = self.alloc_block()
                self._write_ptr(inode.single, logical, ptr)
            return ptr

        logical -= PTRS_PER_BLOCK
        if logical < PTRS_PER_BLOCK * PTRS_PER_BLOCK:
            if inode.double == 0:
                inode.double = self.alloc_block()
                self.disk.write_block(inode.double, b"\x00" * DEFAULT_BLOCK_SIZE)
                self.write_inode(ino, inode)
            outer = logical // PTRS_PER_BLOCK
            inner = logical % PTRS_PER_BLOCK
            inner_block = self._read_ptr(inode.double, outer)
            if inner_block == 0:
                inner_block = self.alloc_block()
                self.disk.write_block(inner_block, b"\x00" * DEFAULT_BLOCK_SIZE)
                self._write_ptr(inode.double, outer, inner_block)
            ptr = self._read_ptr(inner_block, inner)
            if ptr == 0:
                ptr = self.alloc_block()
                self._write_ptr(inner_block, inner, ptr)
            return ptr
        raise FSError("逻辑块号超出最大文件大小")

    def _free_all_blocks(self, inode: Inode) -> None:
        """释放 inode 所有的数据块和间接块。"""
        # 直接块
        for i in range(DIRECT_COUNT):
            if inode.direct[i]:
                self.free_block(inode.direct[i])
                inode.direct[i] = 0
        # 一级间接
        if inode.single:
            for i in range(PTRS_PER_BLOCK):
                ptr = self._read_ptr(inode.single, i)
                if ptr:
                    self.free_block(ptr)
            self.free_block(inode.single)
            inode.single = 0
        # 二级间接
        if inode.double:
            for i in range(PTRS_PER_BLOCK):
                inner = self._read_ptr(inode.double, i)
                if inner:
                    for j in range(PTRS_PER_BLOCK):
                        ptr = self._read_ptr(inner, j)
                        if ptr:
                            self.free_block(ptr)
                    self.free_block(inner)
            self.free_block(inode.double)
            inode.double = 0

    # ---- 目录操作 ----
    def _dir_entries_block(self, block_no: int) -> List[Tuple[int, int, str]]:
        data = self.disk.read_block(block_no)
        out = []
        for i in range(DEFAULT_BLOCK_SIZE // DIR_ENTRY_SIZE):
            raw = data[i * DIR_ENTRY_SIZE : (i + 1) * DIR_ENTRY_SIZE]
            ino, t, name = struct.unpack(DIR_ENTRY_FORMAT, raw[:DIR_ENTRY_PACKED_SIZE])
            if ino != 0:
                out.append((ino, t, _decode_name(name)))
        return out

    @_read_locked
    def dir_list(self, dir_ino: int) -> List[Tuple[str, int, int]]:
        """返回 [(name, ino, type), ...]。"""
        inode = self.read_inode(dir_ino)
        if inode.type != T_DIR:
            raise FSError(f"inode {dir_ino} 不是目录")
        result = []
        nblocks = _ceil_div(inode.size, DEFAULT_BLOCK_SIZE) or 1
        for logical in range(nblocks):
            bno = self._get_block_ptr(inode, logical)
            if bno == 0:
                continue
            for ino, t, name in self._dir_entries_block(bno):
                result.append((name, ino, t))
        return result

    @_read_locked
    def dir_lookup(self, dir_ino: int, name: str) -> Optional[Tuple[int, int]]:
        for n, ino, t in self.dir_list(dir_ino):
            if n == name:
                return ino, t
        return None

    def _find_free_dir_slot(self, inode: Inode, ino: int) -> Tuple[int, int]:
        """在目录里找一个空闲槽位 (block_no, slot_index)，必要时扩展目录。"""
        nblocks = _ceil_div(inode.size, DEFAULT_BLOCK_SIZE) or 1
        for logical in range(nblocks):
            bno = self._get_block_ptr(inode, logical)
            if bno == 0:
                continue
            data = self.disk.read_block(bno)
            for i in range(DEFAULT_BLOCK_SIZE // DIR_ENTRY_SIZE):
                raw = data[i * DIR_ENTRY_SIZE : (i + 1) * DIR_ENTRY_SIZE]
                existing_ino = struct.unpack_from("<I", raw)[0]
                if existing_ino == 0:
                    return bno, i
        # 扩展目录
        logical = nblocks
        bno = self._ensure_block_ptr(ino, inode, logical)
        self.disk.write_block(bno, b"\x00" * DEFAULT_BLOCK_SIZE)
        inode.size = (logical + 1) * DEFAULT_BLOCK_SIZE
        inode.mtime = int(time.time())
        self.write_inode(ino, inode)
        return bno, 0

    @_write_locked
    def dir_add_entry(self, dir_ino: int, name: str, target_ino: int, target_type: int) -> None:
        if name in (".", ".."):
            raise FSError("不能手动添加 . 或 .. 目录项")
        inode = self.read_inode(dir_ino)
        if inode.type != T_DIR:
            raise FSError(f"inode {dir_ino} 不是目录")
        if self.dir_lookup(dir_ino, name):
            raise FSError(f"目录项已存在: {name}")
        bno, slot = self._find_free_dir_slot(inode, dir_ino)
        data = bytearray(self.disk.read_block(bno))
        entry = struct.pack(DIR_ENTRY_FORMAT, target_ino, target_type, _encode_name(name))
        data[slot * DIR_ENTRY_SIZE : slot * DIR_ENTRY_SIZE + DIR_ENTRY_PACKED_SIZE] = entry
        self.disk.write_block(bno, bytes(data))
        inode.mtime = int(time.time())
        self.write_inode(dir_ino, inode)

    @_write_locked
    def dir_remove_entry(self, dir_ino: int, name: str) -> Optional[Tuple[int, int]]:
        """删除目录项，返回 (ino, type)。不存在返回 None。"""
        inode = self.read_inode(dir_ino)
        if inode.type != T_DIR:
            raise FSError(f"inode {dir_ino} 不是目录")
        nblocks = _ceil_div(inode.size, DEFAULT_BLOCK_SIZE) or 1
        for logical in range(nblocks):
            bno = self._get_block_ptr(inode, logical)
            if bno == 0:
                continue
            data = bytearray(self.disk.read_block(bno))
            for i in range(DEFAULT_BLOCK_SIZE // DIR_ENTRY_SIZE):
                off = i * DIR_ENTRY_SIZE
                raw = data[off : off + DIR_ENTRY_PACKED_SIZE]
                e_ino, e_type, e_name = struct.unpack(DIR_ENTRY_FORMAT, raw)
                if e_ino != 0 and _decode_name(e_name) == name:
                    # 清空这一项
                    data[off : off + DIR_ENTRY_PACKED_SIZE] = b"\x00" * DIR_ENTRY_PACKED_SIZE
                    self.disk.write_block(bno, bytes(data))
                    inode.mtime = int(time.time())
                    self.write_inode(dir_ino, inode)
                    return e_ino, e_type
        return None

    # ---- 路径解析 ----
    def _split_path(self, path: str) -> List[str]:
        parts = []
        for p in path.replace("\\", "/").split("/"):
            if p and p != ".":
                parts.append(p)
        return parts

    @_read_locked
    def resolve(self, path: str, follow: bool = True, max_depth: int = 40) -> int:
        """解析路径，返回 inode 号。

        follow=True（默认，类似 stat）：若末尾组件是符号链接则跟踪到底。
        follow=False（类似 lstat）：返回符号链接自身的 inode。
        中间路径上的符号链接始终被跟踪。含循环检测。
        """
        parts = list(self._split_path(path))
        if not parts:
            return ROOT_INO
        cur = ROOT_INO  # 当前所在目录
        followed = 0
        i = 0
        while i < len(parts):
            p = parts[i]
            res = self.dir_lookup(cur, p)
            if res is None:
                raise FSError(f"路径不存在: {path}")
            child_ino, child_type = res
            is_last = i == len(parts) - 1
            if child_type == T_SYMLINK and (not is_last or follow):
                followed += 1
                if followed > max_depth:
                    raise FSError("符号链接层数过多（可能存在循环）")
                target = self.readlink(child_ino)
                target_parts = self._split_path(target)
                if target.startswith("/"):
                    cur = ROOT_INO
                # 相对目标基于当前目录 cur（即符号链接所在目录）
                parts = target_parts + parts[i + 1:]
                i = 0
                continue
            cur = child_ino
            i += 1
        return cur

    @_read_locked
    def resolve_parent(self, path: str) -> Tuple[int, str]:
        parts = self._split_path(path)
        if not parts:
            raise FSError("不能对根目录做此操作")
        parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        # 父路径中的符号链接总是被跟踪
        parent_ino = self.resolve(parent_path, follow=True)
        return parent_ino, parts[-1]

    # ---- 硬链接 / 属性 ----
    @_write_locked
    def link(self, old_path: str, new_path: str) -> int:
        """创建硬链接。目标 inode 的 nlink +1。"""
        ino = self.resolve(old_path, follow=True)
        inode = self.read_inode(ino)
        if inode.type == T_DIR:
            raise FSError("不允许对目录创建硬链接")
        parent_ino, name = self.resolve_parent(new_path)
        if self.dir_lookup(parent_ino, name):
            raise FSError(f"目标已存在: {new_path}")
        self.dir_add_entry(parent_ino, name, ino, inode.type)
        inode.nlink += 1
        inode.ctime = int(time.time())
        self.write_inode(ino, inode)
        return ino

    @_write_locked
    def chmod(self, ino: int, mode: int) -> None:
        inode = self.read_inode(ino)
        inode.mode = mode & 0o7777
        inode.ctime = int(time.time())
        self.write_inode(ino, inode)

    @_write_locked
    def chown(self, ino: int, uid: int = -1, gid: int = -1) -> None:
        inode = self.read_inode(ino)
        if uid >= 0:
            inode.uid = uid
        if gid >= 0:
            inode.gid = gid
        inode.ctime = int(time.time())
        self.write_inode(ino, inode)

    @_write_locked
    def utime(self, ino: int, atime: int = -1, mtime: int = -1) -> None:
        now = int(time.time())
        inode = self.read_inode(ino)
        inode.atime = now if atime < 0 else atime
        inode.mtime = now if mtime < 0 else mtime
        self.write_inode(ino, inode)

    @_read_locked
    def access(self, ino: int, mode: int, uid: int = 0, gid: int = 0) -> bool:
        """检查 uid/gid 对 inode 是否有 mode 权限（r=4,w=2,x=1）。

        uid=0（root）总是允许。
        """
        if uid == 0:
            return True
        st = self.stat(ino)
        perms = st.mode & 0o777
        if st.uid == uid:
            file_perms = (perms >> 6) & 7
        elif st.gid == gid:
            file_perms = (perms >> 3) & 7
        else:
            file_perms = perms & 7
        return (file_perms & mode) == mode

    # ---- 创建 / 删除 ----
    def _create_node(self, parent_ino: int, name: str, node_type: int,
                     mode: int = 0o644) -> int:
        now = int(time.time())
        new_ino = self.alloc_inode()
        inode = Inode.empty()
        inode.type = node_type
        if node_type == T_FILE:
            inode.mode = mode
        elif node_type == T_DIR:
            # 目录必须可执行（遍历）。组/其他位按调用方 mode，再强制加 x；
            # 属主位取调用方原样（不强制覆盖，避免剥夺用户限制）。
            inode.mode = (
                (mode & 0o700)
                | (mode & 0o070) | 0o010
                | (mode & 0o007) | 0o001
            )
        else:
            # symlink 等其它类型：mode 由调用方控制
            inode.mode = mode
        inode.nlink = 1 if node_type != T_DIR else 2  # 自身 + ".."
        inode.uid = 0
        inode.gid = 0
        inode.size = 0
        inode.atime = now
        inode.mtime = now
        inode.ctime = now
        self.write_inode(new_ino, inode)

        if node_type == T_DIR:
            # 初始化目录：写入 . 和 ..
            bno = self.alloc_block()
            self.disk.write_block(bno, b"\x00" * DEFAULT_BLOCK_SIZE)
            data = bytearray(self.disk.read_block(bno))
            dot = struct.pack(DIR_ENTRY_FORMAT, new_ino, T_DIR, _encode_name("."))
            ddot = struct.pack(DIR_ENTRY_FORMAT, parent_ino, T_DIR, _encode_name(".."))
            data[0:DIR_ENTRY_PACKED_SIZE] = dot
            data[DIR_ENTRY_PACKED_SIZE : 2 * DIR_ENTRY_PACKED_SIZE] = ddot
            self.disk.write_block(bno, bytes(data))
            di = self.read_inode(new_ino)
            di.direct[0] = bno
            di.size = DEFAULT_BLOCK_SIZE
            self.write_inode(new_ino, di)
            # 父目录 nlink +1
            p = self.read_inode(parent_ino)
            p.nlink += 1
            self.write_inode(parent_ino, p)

        self.dir_add_entry(parent_ino, name, new_ino, node_type)
        return new_ino

    @_write_locked
    def create(self, path: str, mode: int = 0o644) -> int:
        parent_ino, name = self.resolve_parent(path)
        return self._create_node(parent_ino, name, T_FILE, mode)

    @_write_locked
    def mkdir(self, path: str, mode: int = 0o755) -> int:
        parent_ino, name = self.resolve_parent(path)
        return self._create_node(parent_ino, name, T_DIR, mode)

    @_write_locked
    def symlink(self, target: str, linkpath: str) -> int:
        parent_ino, name = self.resolve_parent(linkpath)
        new_ino = self._create_node(parent_ino, name, T_SYMLINK, 0o777)
        # 把 target 存到 inode 的数据块里
        self.write_file(new_ino, 0, target.encode("utf-8"))
        return new_ino

    @_read_locked
    def readlink(self, ino: int) -> str:
        inode = self.read_inode(ino)
        if inode.type != T_SYMLINK:
            raise FSError(f"inode {ino} 不是符号链接")
        data = self.read_file(ino, 0, inode.size)
        return data.decode("utf-8", errors="replace")

    @_write_locked
    def unlink(self, path: str) -> None:
        parent_ino, name = self.resolve_parent(path)
        inode = self.read_inode(parent_ino)
        if inode.type != T_DIR:
            raise FSError("父路径不是目录")
        res = self.dir_lookup(parent_ino, name)
        if res is None:
            raise FSError(f"文件不存在: {path}")
        target_ino, target_type = res
        if target_type == T_DIR:
            raise FSError(f"是目录，请用 rmdir: {path}")
        self._remove_node(parent_ino, name, target_ino)

    @_write_locked
    def rmdir(self, path: str) -> None:
        parent_ino, name = self.resolve_parent(path)
        res = self.dir_lookup(parent_ino, name)
        if res is None:
            raise FSError(f"目录不存在: {path}")
        target_ino, target_type = res
        if target_type != T_DIR:
            raise FSError(f"不是目录: {path}")
        if self.dir_list(target_ino):
            # 允许 . 和 ..
            real = [e for e in self.dir_list(target_ino) if e[0] not in (".", "..")]
            if real:
                raise FSError(f"目录非空: {path}")
        # 父目录 nlink -1
        p = self.read_inode(parent_ino)
        p.nlink = max(0, p.nlink - 1)
        self.write_inode(parent_ino, p)
        self._remove_node(parent_ino, name, target_ino)

    def _remove_node(self, parent_ino: int, name: str, target_ino: int) -> None:
        self.dir_remove_entry(parent_ino, name)
        inode = self.read_inode(target_ino)
        inode.nlink -= 1
        if inode.nlink <= 0:
            self._free_all_blocks(inode)
            inode.type = T_FREE
            inode.size = 0
            self.write_inode(target_ino, inode)
            self.free_inode(target_ino)
        else:
            self.write_inode(target_ino, inode)

    @_write_locked
    def rename(self, src: str, dst: str) -> None:
        sp, sname = self.resolve_parent(src)
        dp, dname = self.resolve_parent(dst)
        res = self.dir_lookup(sp, sname)
        if res is None:
            raise FSError(f"源不存在: {src}")
        target_ino, target_type = res
        # 如果 dst 已存在
        existing = self.dir_lookup(dp, dname)
        if existing is not None:
            ex_ino, ex_type = existing
            if target_type == T_DIR and ex_type != T_DIR:
                raise FSError("目标已存在且不是目录")
            if target_type != T_DIR and ex_type == T_DIR:
                raise FSError("目标已存在且是目录")
            # 删除目标
            if ex_type == T_DIR:
                self.rmdir(dst)
            else:
                self.unlink(dst)
        self.dir_remove_entry(sp, sname)
        self.dir_add_entry(dp, dname, target_ino, target_type)
        # 如果是目录且跨父目录，更新 ..
        if target_type == T_DIR and sp != dp:
            ti = self.read_inode(target_ino)
            # 更新 .. 项
            bno = ti.direct[0]
            data = bytearray(self.disk.read_block(bno))
            ddot = struct.pack(DIR_ENTRY_FORMAT, dp, T_DIR, _encode_name(".."))
            data[DIR_ENTRY_PACKED_SIZE : 2 * DIR_ENTRY_PACKED_SIZE] = ddot
            self.disk.write_block(bno, bytes(data))

    # ---- 文件读写 ----
    @_read_locked
    def read_file(self, ino: int, offset: int, length: int) -> bytes:
        # 注意：为支持多读者并发，读操作不更新 atime（类似 noatime 挂载）。
        if length <= 0:
            return b""
        inode = self.read_inode(ino)
        if offset >= inode.size:
            return b""
        avail = inode.size - offset
        length = min(length, avail)
        out = bytearray()
        remaining = length
        cur = offset
        while remaining > 0:
            logical = cur // DEFAULT_BLOCK_SIZE
            in_block = cur % DEFAULT_BLOCK_SIZE
            chunk = min(remaining, DEFAULT_BLOCK_SIZE - in_block)
            bno = self._get_block_ptr(inode, logical)
            if bno == 0:
                out.extend(b"\x00" * chunk)
            else:
                data = self.disk.read_block(bno)
                out.extend(data[in_block : in_block + chunk])
            cur += chunk
            remaining -= chunk
        return bytes(out)

    @_write_locked
    def append_path(self, path: str, data: bytes, mode: int = 0o644) -> int:
        """原子追加到路径：在写锁内完成"解析/创建 + 读 size + 写入"。

        供多线程并发追加使用，避免 stat 与 write 之间的 TOCTOU 竞态
        （先读到 size，再写入时别的线程已追加，导致覆盖而非追加）。
        """
        if not data:
            return 0
        try:
            ino = self.resolve(path)
        except FSError:
            ino = self.create(path, mode)
        inode = self.read_inode(ino)
        # write_file 自身 @_write_locked，同线程重入，安全。
        self.write_file(ino, inode.size, data)
        return len(data)

    @_write_locked
    def write_path(self, path: str, data: bytes, mode: int = 0o644) -> int:
        """原子覆盖写路径：在写锁内完成"解析/创建 + 截断 + 写入"。

        避免并发覆盖写时 exists/resolve 与 truncate/write 之间的竞态。
        """
        try:
            ino = self.resolve(path)
            self.truncate(ino, 0)
        except FSError:
            ino = self.create(path, mode)
        self.write_file(ino, 0, data)
        return len(data)

    @_write_locked
    def write_file(self, ino: int, offset: int, data: bytes) -> int:
        if not data:
            return 0
        inode = self.read_inode(ino)
        total = len(data)
        cur = offset
        pos = 0
        while pos < total:
            logical = cur // DEFAULT_BLOCK_SIZE
            in_block = cur % DEFAULT_BLOCK_SIZE
            chunk = min(total - pos, DEFAULT_BLOCK_SIZE - in_block)
            bno = self._ensure_block_ptr(ino, inode, logical)
            block = bytearray(self.disk.read_block(bno))
            block[in_block : in_block + chunk] = data[pos : pos + chunk]
            self.disk.write_block(bno, bytes(block))
            pos += chunk
            cur += chunk
            # write_inode 可能在 _ensure_block_ptr 内已写过，这里重新读最新值
            inode = self.read_inode(ino)
        if offset + total > inode.size:
            inode.size = offset + total
        now = int(time.time())
        inode.mtime = now
        inode.ctime = now
        self.write_inode(ino, inode)
        return total

    @_write_locked
    def truncate(self, ino: int, size: int) -> None:
        if size < 0:
            raise FSError("大小不能为负")
        inode = self.read_inode(ino)
        if size == inode.size:
            return
        if size < inode.size:
            new_blocks = _ceil_div(size, DEFAULT_BLOCK_SIZE) if size > 0 else 0
            old_blocks = _ceil_div(inode.size, DEFAULT_BLOCK_SIZE)
            # 释放多余的完整数据块
            for logical in range(new_blocks, old_blocks):
                bno = self._get_block_ptr(inode, logical)
                if bno:
                    self.free_block(bno)
                    self._clear_block_ptr(inode, logical)
            # 若间接块已全部空闲，则释放它们
            self._maybe_free_indirect(ino, inode, new_blocks)
            inode.size = size
        else:
            # 扩大：不预分配块，读取空洞时返回 0（稀疏文件）
            inode.size = size
        now = int(time.time())
        inode.mtime = now
        inode.ctime = now
        self.write_inode(ino, inode)

    def _clear_block_ptr(self, inode: Inode, logical: int) -> None:
        """把逻辑块指针置 0（仅改内存 inode 与间接块，不写 inode）。"""
        if logical < DIRECT_COUNT:
            inode.direct[logical] = 0
            return
        logical -= DIRECT_COUNT
        if logical < PTRS_PER_BLOCK:
            if inode.single:
                self._write_ptr(inode.single, logical, 0)
            return
        logical -= PTRS_PER_BLOCK
        if inode.double:
            outer = logical // PTRS_PER_BLOCK
            inner = logical % PTRS_PER_BLOCK
            inner_block = self._read_ptr(inode.double, outer)
            if inner_block:
                self._write_ptr(inner_block, inner, 0)

    def _maybe_free_indirect(self, ino: int, inode: Inode, keep_blocks: int) -> None:
        """当直接块/间接块范围内的数据块全空时，释放间接块结构本身。"""
        # 一级间接：仅当 keep_blocks <= DIRECT_COUNT 时才可能完全空闲
        if inode.single and keep_blocks <= DIRECT_COUNT:
            all_zero = True
            for i in range(PTRS_PER_BLOCK):
                if self._read_ptr(inode.single, i):
                    all_zero = False
                    break
            if all_zero:
                self.free_block(inode.single)
                inode.single = 0
        # 二级间接：仅当 keep_blocks <= DIRECT_COUNT + PTRS_PER_BLOCK 时才可能完全空闲
        if inode.double and keep_blocks <= DIRECT_COUNT + PTRS_PER_BLOCK:
            all_zero = True
            for i in range(PTRS_PER_BLOCK):
                if self._read_ptr(inode.double, i):
                    all_zero = False
                    break
            if all_zero:
                # 内部间接块也应已在上面的数据块释放中被 free
                self.free_block(inode.double)
                inode.double = 0

    # ---- 查询 ----
    @_read_locked
    def stat(self, ino: int) -> Stat:
        i = self.read_inode(ino)
        return Stat(
            ino=ino,
            type=i.type,
            mode=i.mode,
            nlink=i.nlink,
            size=i.size,
            uid=i.uid,
            gid=i.gid,
            atime=i.atime,
            mtime=i.mtime,
            ctime=i.ctime,
        )

    @_read_locked
    def stat_path(self, path: str, follow: bool = True) -> Stat:
        return self.stat(self.resolve(path, follow=follow))

    @_read_locked
    def lstat_path(self, path: str) -> Stat:
        """不跟踪末尾符号链接（类似 lstat）。"""
        return self.stat_path(path, follow=False)

    # ---- 空间统计 ----
    @_read_locked
    def count_free_blocks(self) -> int:
        assert self.sb is not None
        used = 0
        for i in range(self.sb.total_blocks):
            if self._bitmap_get(self.sb.block_bitmap_start, i):
                used += 1
        return self.sb.total_blocks - used

    @_read_locked
    def count_free_inodes(self) -> int:
        assert self.sb is not None
        used = 0
        for i in range(self.sb.total_inodes):
            if self._bitmap_get(self.sb.inode_bitmap_start, i):
                used += 1
        return self.sb.total_inodes - used

    @_read_locked
    def statfs(self) -> dict:
        """返回文件系统使用情况（类似 statfs）。"""
        assert self.sb is not None
        free_blocks = self.count_free_blocks()
        free_inodes = self.count_free_inodes()
        return {
            "bsize": self.sb.block_size,
            "blocks": self.sb.total_blocks,
            "bfree": free_blocks,
            "bavail": free_blocks,
            "files": self.sb.total_inodes,
            "ffree": free_inodes,
            "favail": free_inodes,
            "data_blocks": self.sb.data_blocks,
            "data_start": self.sb.data_start,
        }

    # ---- fsck 一致性检查 ----
    def fsck(self, repair: bool = False) -> dict:
        """检查文件系统一致性。返回问题报告。

        repair=True 时尝试修复可自动修复的问题（取写锁）；repair=False 只读检查（取读锁）。
        """
        assert self.sb is not None
        # 根据是否修复选择读/写锁
        lock_ctx = self._lock.write() if repair else self._lock.read()
        with lock_ctx:
            return self._fsck_impl(repair)

    def _fsck_impl(self, repair: bool) -> dict:
        sb = self.sb
        problems: list = []
        repaired: list = []

        if sb.magic != MAGIC:
            problems.append("致命：超级块魔数不匹配")
            return {"ok": False, "problems": problems, "repaired": repaired}

        # 收集每个 inode 被目录引用的次数（硬链接计数）
        ref_count = [0] * sb.total_inodes
        # 收集每个 inode 实际引用的数据块
        used_blocks: set = set()
        # 保留区块
        for b in range(0, sb.data_start):
            used_blocks.add(b)

        # 遍历所有已分配 inode（跳过保留的 inode 0）
        for ino in range(1, sb.total_inodes):
            if not self._bitmap_get(sb.inode_bitmap_start, ino):
                continue
            inode = self.read_inode(ino)
            if inode.type == T_FREE:
                problems.append(f"inode {ino}: 位图标记已用但类型为 FREE")
                if repair:
                    self.free_inode(ino)
                    repaired.append(f"释放 inode {ino}")
                continue
            # 校验块指针都在范围内且标记为已用
            nblocks = _ceil_div(inode.size, DEFAULT_BLOCK_SIZE) if inode.type != T_DIR else _ceil_div(inode.size, DEFAULT_BLOCK_SIZE) or 1
            for logical in range(nblocks):
                bno = self._get_block_ptr(inode, logical)
                if bno == 0:
                    continue
                if bno < 0 or bno >= sb.total_blocks:
                    problems.append(f"inode {ino}: 块指针 {bno} 越界")
                    continue
                if bno in used_blocks:
                    problems.append(f"inode {ino}: 块 {bno} 被多个 inode 共享")
                used_blocks.add(bno)
                if not self._bitmap_get(sb.block_bitmap_start, bno):
                    problems.append(f"inode {ino}: 块 {bno} 未在位图中标记")
                    if repair:
                        self._bitmap_set(sb.block_bitmap_start, bno, True)
                        repaired.append(f"标记块 {bno} 为已用")
            # 间接块本身
            for meta_bno in (inode.single, inode.double):
                if meta_bno:
                    if not self._bitmap_get(sb.block_bitmap_start, meta_bno):
                        problems.append(f"inode {ino}: 间接块 {meta_bno} 未标记")
                        if repair:
                            self._bitmap_set(sb.block_bitmap_start, meta_bno, True)
                            repaired.append(f"标记间接块 {meta_bno}")

        # 遍历目录，统计引用（包含 "." 和 ".."，因为它们也是硬链接）
        for ino in range(sb.total_inodes):
            if not self._bitmap_get(sb.inode_bitmap_start, ino):
                continue
            inode = self.read_inode(ino)
            if inode.type != T_DIR:
                continue
            for name, child_ino, _t in self.dir_list(ino):
                if child_ino >= sb.total_inodes or not self._bitmap_get(sb.inode_bitmap_start, child_ino):
                    if name not in (".", ".."):
                        problems.append(f"目录 inode {ino}: 项 {name!r} 指向无效 inode {child_ino}")
                    continue
                ref_count[child_ino] += 1

        # 检查 nlink 一致性（跳过保留的 inode 0）
        for ino in range(1, sb.total_inodes):
            if not self._bitmap_get(sb.inode_bitmap_start, ino):
                continue
            inode = self.read_inode(ino)
            expected = ref_count[ino]
            if expected == 0:
                problems.append(f"inode {ino}: 已分配但无任何目录引用（孤儿）")
            if inode.nlink != expected:
                problems.append(
                    f"inode {ino}: nlink={inode.nlink} 但实际引用数={expected}"
                )
                if repair:
                    inode.nlink = max(1, expected)
                    self.write_inode(ino, inode)
                    repaired.append(f"修正 inode {ino} nlink -> {inode.nlink}")

        # 检查孤儿块（位图标记已用但无 inode 引用）
        for b in range(sb.data_start, sb.total_blocks):
            if self._bitmap_get(sb.block_bitmap_start, b) and b not in used_blocks:
                problems.append(f"块 {b}: 标记已用但无 inode 引用（孤儿块）")
                if repair:
                    self._bitmap_set(sb.block_bitmap_start, b, False)
                    repaired.append(f"释放孤儿块 {b}")

        # 检查根目录
        root = self.read_inode(ROOT_INO)
        if root.type != T_DIR:
            problems.append("致命：根 inode 不是目录")

        return {
            "ok": len(problems) == 0,
            "problems": problems,
            "repaired": repaired,
        }


def grow(disk: VirtualDisk, new_size: int) -> SuperBlock:
    """扩大磁盘镜像容量（在线扩容，不破坏数据）。

    仅当块位图有足够容量时支持（即新增块数不超过位图剩余容量）。
    """
    disk.open()
    fs = FS(disk).mount()
    sb = fs.sb
    old_blocks = sb.total_blocks
    new_blocks = new_size // sb.block_size
    if new_blocks <= old_blocks:
        raise FSError(f"新大小不大于当前大小（当前 {old_blocks} 块）")
    bitmap_capacity = sb.block_bitmap_blocks * sb.block_size * 8
    if new_blocks > bitmap_capacity:
        raise FSError(
            f"块位图容量不足：最多支持 {bitmap_capacity} 块，请求 {new_blocks} 块。"
            f"请重新创建更大的磁盘。"
        )
    # 扩展文件（走 disk 接口而非内部 _f，保持层间一致）
    disk.truncate_bytes(new_blocks * sb.block_size)
    # 更新超级块
    sb.total_blocks = new_blocks
    sb.data_blocks = new_blocks - sb.data_start
    # 读-改-写：保留 block 0 末尾的磁盘身份尾标
    raw = bytearray(disk.read_block(0))
    sb_bytes = sb.to_bytes()
    raw[:len(sb_bytes)] = sb_bytes
    disk.write_block(0, bytes(raw))
    disk.flush()
    return sb


def mkfs(disk: VirtualDisk, total_inodes: Optional[int] = None,
         label: str = "", disk_uuid: Optional[str] = None) -> SuperBlock:
    """在一个 VirtualDisk 上格式化文件系统。

    label:     该盘的卷标（模拟驱动按卷标识别 / 挂载）
    disk_uuid: 该盘自己的 UUID；不指定则自动生成。会写入 block 0 末尾的身份尾标。
    """
    from .identity import write_identity_to_block0, new_disk_uuid
    disk.open()
    nblocks = disk.nblocks
    if nblocks < 16:
        raise FSError("磁盘太小")

    # 默认 inode 数量：每 4 个块 1 个 inode，上限和块数相同
    if total_inodes is None:
        total_inodes = max(16, min(nblocks, nblocks // 4))

    block_size = DEFAULT_BLOCK_SIZE
    inode_bitmap_blocks = _ceil_div(total_inodes, block_size * 8)
    block_bitmap_blocks = _ceil_div(nblocks, block_size * 8)
    inode_table_blocks = _ceil_div(total_inodes * INODE_SIZE, block_size)

    cur = 1
    inode_bitmap_start = cur
    cur += inode_bitmap_blocks
    block_bitmap_start = cur
    cur += block_bitmap_blocks
    inode_table_start = cur
    cur += inode_table_blocks
    data_start = cur
    data_blocks = nblocks - data_start

    if data_blocks <= 0:
        raise FSError("磁盘太小，没有数据块")

    sb = SuperBlock(
        magic=MAGIC,
        version=VERSION,
        block_size=block_size,
        total_blocks=nblocks,
        total_inodes=total_inodes,
        inode_size=INODE_SIZE,
        inode_bitmap_start=inode_bitmap_start,
        inode_bitmap_blocks=inode_bitmap_blocks,
        block_bitmap_start=block_bitmap_start,
        block_bitmap_blocks=block_bitmap_blocks,
        inode_table_start=inode_table_start,
        inode_table_blocks=inode_table_blocks,
        data_start=data_start,
        data_blocks=data_blocks,
        root_inode=ROOT_INO,
        created=int(time.time()),
    )
    disk.write_block(0, sb.to_bytes())

    # 初始化所有位图块和 inode 表块为 0
    for b in range(inode_bitmap_start, data_start):
        disk.write_block(b, b"\x00" * block_size)

    fs = FS(disk)
    fs.sb = sb

    # inode 0 保留（不使用），标记为已用
    fs._bitmap_set(inode_bitmap_start, 0, True)

    # 创建根目录 inode (ROOT_INO = 1)
    root = Inode.empty()
    root.type = T_DIR
    root.mode = 0o755
    root.nlink = 2  # "." + ".."（根的 ".." 指向自身）
    root.uid = 0
    root.gid = 0
    root.size = DEFAULT_BLOCK_SIZE
    fs.write_inode(ROOT_INO, root)
    fs._bitmap_set(inode_bitmap_start, ROOT_INO, True)

    # 根目录的数据块，写 . 和 ..
    bno = fs.alloc_block()
    data = bytearray(b"\x00" * block_size)
    dot = struct.pack(DIR_ENTRY_FORMAT, ROOT_INO, T_DIR, _encode_name("."))
    ddot = struct.pack(DIR_ENTRY_FORMAT, ROOT_INO, T_DIR, _encode_name(".."))
    data[0:DIR_ENTRY_PACKED_SIZE] = dot
    data[DIR_ENTRY_PACKED_SIZE : 2 * DIR_ENTRY_PACKED_SIZE] = ddot
    disk.write_block(bno, bytes(data))
    root.direct[0] = bno
    fs.write_inode(ROOT_INO, root)

    # 标记保留区为已用（超级块 + 位图 + inode表）
    for b in range(0, data_start):
        fs._bitmap_set(block_bitmap_start, b, True)

    # 写入磁盘身份尾标（block 0 末尾），让模拟驱动能识别本盘
    duuid = disk_uuid or new_disk_uuid()
    try:
        write_identity_to_block0(disk, duuid, vol_id="", label=label,
                                 is_member=False)
    except Exception:
        # 尾标写入失败不阻断格式化（兼容只读等场景）
        pass

    disk.flush()
    return sb
