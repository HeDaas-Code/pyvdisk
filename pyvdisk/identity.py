"""磁盘身份标识：每块 .vdisk 文件都带一个统一的识别码。

设计要点
--------
- 不再用文件路径作为索引。每块盘（无论是单盘文件系统还是多盘卷的成员盘）
  在 block 0 的末尾保存一个 112 字节的 **身份尾标**（DiskIdentity trailer），
  含该盘自己的 UUID、所属卷 ID（单盘为空）和卷标。
- 模拟驱动（DiskManager）扫描一个目录时，读取每块盘的尾标即可识别其身份，
  再按 vol_id 把成员盘组装成完整卷，按卷标挂载——盘文件被复制 / 移动到
  目录里就能被识别，无需关心路径。

尾标布局（block 0 的最后 DISK_ID_TRAILER_SIZE 字节）：
    magic(4) "VDID" + version(2) + flags(2) + disk_uuid(36) + vol_id(36) + label(32)
    = 112 字节

flags:
    bit 0  is_volume_member  该盘是多盘卷的成员盘
"""

from __future__ import annotations

import os
import struct
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Optional

from .disk import DEFAULT_BLOCK_SIZE

# 单盘文件系统魔数（与 fs.MAGIC 一致，避免循环导入在此重复定义）
FS_MAGIC = b"VDK1"
# 卷成员盘魔数（与 volume.VOL_MAGIC 一致）
VOL_MAGIC = b"VDV1"

DISK_ID_MAGIC = b"VDID"
DISK_ID_VERSION = 1
DISK_ID_TRAILER_SIZE = 112
DISK_ID_FORMAT = "<4sHH36s36s32s"  # magic version flags disk_uuid vol_id label

FLAG_MEMBER = 0x0001
FLAG_VECTOR = 0x0002
FLAG_LOG = 0x0004
DISK_EXT = ".vdisk"


def validate_disk_path(path: str) -> None:
    """要求用户可见的磁盘容器统一使用 .vdisk 后缀。"""
    if not str(path).lower().endswith(DISK_EXT):
        raise ValueError(f"虚拟磁盘文件必须使用 {DISK_EXT} 后缀: {path}")


class IdentityError(Exception):
    pass


def _pad_str(s: str, n: int) -> bytes:
    b = (s or "").encode("utf-8")
    if len(b) > n:
        b = b[:n]
    return b + b"\x00" * (n - len(b))


def _unpad_str(b: bytes) -> str:
    return b.rstrip(b"\x00").decode("utf-8", "replace")


def make_trailer(disk_uuid: str, vol_id: str, label: str,
                 is_member: bool, is_vector: bool = False,
                 is_log: bool = False) -> bytes:
    """构造 112 字节的身份尾标。"""
    flags = ((FLAG_MEMBER if is_member else 0) |
             (FLAG_VECTOR if is_vector else 0) |
             (FLAG_LOG if is_log else 0))
    return struct.pack(
        DISK_ID_FORMAT,
        DISK_ID_MAGIC,
        DISK_ID_VERSION,
        flags,
        _pad_str(disk_uuid, 36),
        _pad_str(vol_id, 36),
        _pad_str(label, 32),
    )


def parse_trailer(block: bytes) -> Optional["DiskIdentity"]:
    """从一块（4096 字节）数据末尾解析身份尾标。

    尾标不存在或魔数不匹配时返回 None。
    """
    if len(block) < DISK_ID_TRAILER_SIZE:
        return None
    tail = block[-DISK_ID_TRAILER_SIZE:]
    try:
        magic, version, flags, duuid, vid, label = struct.unpack(
            DISK_ID_FORMAT, tail
        )
    except struct.error:
        return None
    if magic != DISK_ID_MAGIC:
        return None
    return DiskIdentity(
        path="",
        kind=("member" if (flags & FLAG_MEMBER) else
              "vector" if (flags & FLAG_VECTOR) else
              "log" if (flags & FLAG_LOG) else "single"),
        disk_uuid=_unpad_str(duuid),
        vol_id=_unpad_str(vid),
        label=_unpad_str(label),
        is_member=bool(flags & FLAG_MEMBER),
        is_vector_disk=bool(flags & FLAG_VECTOR),
        is_log_disk=bool(flags & FLAG_LOG),
        trailer_version=version,
    )


@dataclass
class DiskIdentity:
    """一块盘的身份信息（由探测尾标得到）。"""
    path: str = ""
    kind: str = "unknown"          # "single" | "member" | "unknown"
    disk_uuid: str = ""            # 该盘自己的 UUID
    vol_id: str = ""               # 所属卷 ID（单盘为空）
    label: str = ""                # 卷标
    is_member: bool = False
    is_vector_disk: bool = False
    is_log_disk: bool = False
    trailer_version: int = 0
    # 仅 member 有：该盘 block 0 上读到的卷元数据（含完整成员清单）
    vol_meta: Optional[object] = None
    # 仅 single 有：该盘块数（用于显示）
    nblocks: int = 0

    @property
    def is_single(self) -> bool:
        return self.kind == "single"

    @property
    def is_vector(self) -> bool:
        return self.kind == "vector"

    @property
    def is_log(self) -> bool:
        return self.kind == "log"

    @property
    def is_complete_member(self) -> bool:
        """成员盘且能解析出卷元数据。"""
        return self.kind == "member" and self.vol_meta is not None

    def short(self) -> str:
        u = self.disk_uuid[:8] if self.disk_uuid else "????????"
        if self.is_member:
            return f"member[{u}] vol={self.vol_id[:8]}"
        if self.is_single:
            return f"single[{u}]"
        return f"unknown[{u}]"


def write_identity_to_block0(disk, disk_uuid: str, vol_id: str,
                             label: str, is_member: bool,
                             is_vector: bool = False,
                             is_log: bool = False) -> None:
    """把身份尾标写到一块已打开盘的 block 0 末尾（读-改-写，保留前部数据）。"""
    raw = bytearray(disk.read_block(0))
    trailer = make_trailer(disk_uuid, vol_id, label, is_member, is_vector, is_log)
    raw[-DISK_ID_TRAILER_SIZE:] = trailer
    disk.write_block(0, bytes(raw))


def probe_disk(path: str, block_size: int = DEFAULT_BLOCK_SIZE) -> DiskIdentity:
    """探测一个 .vdisk 文件的身份。

    只读取文件第一个块，不打开文件系统。返回 DiskIdentity：
        - block 0 魔数 VDV1 → 多盘卷成员盘（附带卷元数据）
        - block 0 魔数 VDK1 → 单盘文件系统
        - 其它 → unknown（可能不是 vdisk 镜像）
    """
    try:
        with open(path, "rb") as f:
            block = f.read(block_size)
    except OSError:
        return DiskIdentity(path=path, kind="unknown")
    if len(block) < 8:
        return DiskIdentity(path=path, kind="unknown")

    ident = parse_trailer(block) or DiskIdentity(path=path, kind="unknown")
    ident.path = path

    magic = block[:4]
    if magic == VOL_MAGIC:
        # 多盘卷成员盘：解析卷元数据
        from .volume import VolumeMeta
        try:
            meta = VolumeMeta.from_bytes(block)
        except Exception:
            ident.kind = "unknown"
            return ident
        ident.kind = "member"
        ident.is_member = True
        ident.vol_id = meta.vol_id
        ident.label = meta.name
        ident.vol_meta = meta
        # 尾标里的 disk_uuid 才是该盘自己的 uuid
        if not ident.disk_uuid:
            # 老盘没有尾标：用路径兜底
            ident.disk_uuid = "fallback:" + os.path.basename(path)
        return ident
    elif magic == FS_MAGIC:
        ident.kind = ("vector" if ident.is_vector_disk else
                      "log" if ident.is_log_disk else "single")
        ident.is_member = False
        ident.vol_id = ""
        if not ident.disk_uuid:
            ident.disk_uuid = "fallback:" + os.path.basename(path)
        # 记录块数
        try:
            ident.nblocks = os.path.getsize(path) // block_size
        except OSError:
            pass
        return ident
    else:
        return DiskIdentity(path=path, kind="unknown")


def new_disk_uuid() -> str:
    return str(_uuid.uuid4())
