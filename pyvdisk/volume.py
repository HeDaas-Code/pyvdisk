"""多盘融合：把多个虚拟磁盘镜像组合成一个逻辑卷。

支持三种 RAID 模式：
    concat  级联：盘依次拼接，容量 = 各盘之和
    stripe  条带（RAID0）：数据按 stripe_size 轮转分布到各盘，并行度高
    mirror  镜像（RAID1）：多盘互为副本，容量 = 单盘容量，提供冗余

卷的元数据保存在每块盘的第 0 块（卷超级块），描述卷 ID、模式、成员清单、
几何参数等。文件系统的超级块从逻辑块 1 开始（第 0 块预留给卷元数据）。

所有 Volume 实例都实现了与 VirtualDisk 相同的块级/字节级 IO 接口，
因此 FS / mkfs 无需修改即可在其上运行。
"""

from __future__ import annotations

import json
import os
import warnings
import struct
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .disk import VirtualDisk, DEFAULT_BLOCK_SIZE

# 卷元数据魔数
VOL_MAGIC = b"VDV1"
VOL_SB_BLOCK = 0  # 卷超级块固定占逻辑块 0

# 模式
MODE_CONCAT = "concat"
MODE_STRIPE = "stripe"
MODE_MIRROR = "mirror"
VALID_MODES = (MODE_CONCAT, MODE_STRIPE, MODE_MIRROR)

DEFAULT_STRIPE_SIZE = 4096  # 条带单元大小（字节），通常等于一个块


class VolumeError(Exception):
    pass


@dataclass
class DiskMember:
    """卷中的一个成员盘描述。"""
    path: str
    blocks: int  # 该盘的块数
    uuid: str = ""  # 成员 UUID，用于识别

    def to_dict(self) -> dict:
        return {"path": self.path, "blocks": self.blocks, "uuid": self.uuid}

    @classmethod
    def from_dict(cls, d: dict) -> "DiskMember":
        return cls(path=d["path"], blocks=d["blocks"], uuid=d.get("uuid", ""))


@dataclass
class VolumeMeta:
    """卷超级块（保存在每块成员盘的第 0 块）。"""
    magic: bytes = VOL_MAGIC
    version: int = 1
    vol_id: str = ""          # 卷唯一 ID
    name: str = ""            # 卷名
    mode: str = MODE_CONCAT
    stripe_size: int = DEFAULT_STRIPE_SIZE
    block_size: int = DEFAULT_BLOCK_SIZE
    members: List[DiskMember] = field(default_factory=list)
    created: int = 0
    # 运行时计算的几何（不持久化，但缓存于超级块）
    total_blocks: int = 0     # 逻辑总块数（含卷超级块占用的第 0 块）
    data_blocks: int = 0      # 可用数据块数

    def to_dict(self) -> dict:
        return {
            "magic": self.magic.decode("ascii", "replace"),
            "version": self.version,
            "vol_id": self.vol_id,
            "name": self.name,
            "mode": self.mode,
            "stripe_size": self.stripe_size,
            "block_size": self.block_size,
            "members": [m.to_dict() for m in self.members],
            "created": self.created,
            "total_blocks": self.total_blocks,
            "data_blocks": self.data_blocks,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "VolumeMeta":
        return cls(
            magic=d.get("magic", "VDV1").encode("ascii", "replace"),
            version=d.get("version", 1),
            vol_id=d.get("vol_id", ""),
            name=d.get("name", ""),
            mode=d.get("mode", MODE_CONCAT),
            stripe_size=d.get("stripe_size", DEFAULT_STRIPE_SIZE),
            block_size=d.get("block_size", DEFAULT_BLOCK_SIZE),
            members=[DiskMember.from_dict(m) for m in d.get("members", [])],
            created=d.get("created", 0),
            total_blocks=d.get("total_blocks", 0),
            data_blocks=d.get("data_blocks", 0),
        )

    def to_bytes(self) -> bytes:
        raw = json.dumps(self.to_dict(), ensure_ascii=False).encode("utf-8")
        # 前缀：魔数 + 长度 + JSON
        header = struct.pack("<4sI", VOL_MAGIC, len(raw))
        return header + raw

    @classmethod
    def from_bytes(cls, data: bytes) -> "VolumeMeta":
        if len(data) < 8:
            raise VolumeError("卷超级块数据过短")
        magic, length = struct.unpack("<4sI", data[:8])
        if magic != VOL_MAGIC:
            raise VolumeError("不是合法的卷元数据（魔数不匹配）")
        raw = data[8:8 + length]
        d = json.loads(raw.decode("utf-8"))
        return cls.from_dict(d)


class Volume:
    """逻辑卷：把多个 VirtualDisk 聚合为一个块设备。

    与 VirtualDisk 接口兼容：提供 block_size / nblocks / read_block /
    write_block / read_bytes / write_bytes / open / close / flush。
    因此 FS / mkfs 可以直接在其上运行。
    """

    def __init__(self, paths: Optional[List[str]] = None,
                 block_size: int = DEFAULT_BLOCK_SIZE, *, legacy: bool = False):
        if legacy:
            warnings.warn(
                "Volume is a low-level legacy entry point; prefer VFS or DataDisk.",
                DeprecationWarning, stacklevel=2,
            )
        self.block_size = block_size
        self.disks: List[VirtualDisk] = []
        self.meta: Optional[VolumeMeta] = None
        self.nblocks: int = 0
        self._paths = list(paths) if paths else []
        self._member_health: List[dict] = []

    # ---- 几何计算 ----
    @staticmethod
    def compute_geometry(mode: str, member_blocks: List[int],
                         stripe_size: int = DEFAULT_STRIPE_SIZE,
                         block_size: int = DEFAULT_BLOCK_SIZE) -> Tuple[int, int]:
        """根据模式和成员盘块数计算 (total_blocks, data_blocks)。

        每块成员盘的块 0 保留给卷元数据，数据区从块 1 开始。
        total_blocks 是 Volume 暴露给上层的逻辑块数（不含卷元数据块）。
        """
        if not member_blocks:
            return 0, 0
        # 每块盘可用数据块数 = 总块数 - 1（去掉卷元数据块）
        usable = [b - 1 for b in member_blocks]
        if mode == MODE_CONCAT:
            total = sum(usable)
        elif mode == MODE_STRIPE:
            # 条带：以最小盘对齐，每个条带单元 stripe_size 字节
            # stripe_size 应为 block_size 的整数倍
            min_usable = min(usable)
            stripe_blocks = max(1, stripe_size // block_size)
            rounds = min_usable // stripe_blocks
            total = rounds * stripe_blocks * len(member_blocks)
        elif mode == MODE_MIRROR:
            # 镜像：容量 = 最小盘的可用容量
            total = min(usable)
        else:
            raise VolumeError(f"未知模式: {mode}")
        if total < 2:
            raise VolumeError("卷容量不足，至少需要 2 个逻辑块")
        return total, total

    # ---- 生命周期 ----
    def open(self) -> "Volume":
        if self.disks:
            return self
        if not self._paths:
            raise VolumeError("没有成员盘路径")
        # 打开所有成员；镜像允许缺盘降级，其他模式必须全员在线。
        open_errors = {}
        for p in self._paths:
            d = VirtualDisk(p, self.block_size)
            try:
                d.open()
                self.disks.append(d)
            except (OSError, RuntimeError, ValueError) as exc:
                open_errors[p] = str(exc)
                if len(self._paths) < 2:
                    raise
        if not self.disks:
            raise VolumeError("镜像无可用成员盘")
        # 从第一块可用盘读取卷元数据
        first = self.disks[0]
        raw = first.read_block(VOL_SB_BLOCK)
        try:
            self.meta = VolumeMeta.from_bytes(raw)
        except VolumeError as e:
            # 自动关闭已打开的盘
            for d in self.disks:
                d.close()
            self.disks = []
            raise VolumeError(f"读取卷元数据失败: {e}")
        # Only mirror tolerates missing members; concat/stripe mappings require all.
        if open_errors and self.meta.mode != MODE_MIRROR:
            for d in self.disks:
                d.close()
            self.disks = []
            raise VolumeError(f"卷成员不完整: {next(iter(open_errors.values()))}")
        # 校验所有已打开成员；镜像缺盘被明确标记为 degraded。
        self._verify_members()
        self._member_health = []
        for member in self.meta.members:
            disk = next((d for d in self.disks if os.path.abspath(d.path) == os.path.abspath(member.path)), None)
            self._member_health.append({"path": member.path, "healthy": disk is not None, "error": open_errors.get(member.path)})
        self.block_size = self.meta.block_size
        self.nblocks = self.meta.total_blocks
        return self

    def _verify_members(self) -> None:
        assert self.meta is not None
        # 检查每块盘都带有相同的卷 ID
        for i, d in enumerate(self.disks):
            raw = d.read_block(VOL_SB_BLOCK)
            m = VolumeMeta.from_bytes(raw)
            if m.vol_id != self.meta.vol_id:
                raise VolumeError(
                    f"成员盘 {i} ({d.path}) 的卷 ID 不匹配："
                    f"{m.vol_id} != {self.meta.vol_id}"
                )
        # 镜像允许单盘运行（显式 degraded），条带仍要求全部成员。
        if self.meta.mode == MODE_MIRROR and len(self.disks) < 1:
            raise VolumeError("镜像无可用成员盘")
        if self.meta.mode == MODE_STRIPE and len(self.disks) < 2:
            raise VolumeError("条带卷至少需要 2 块盘")

    def close(self) -> None:
        for d in self.disks:
            d.close()
        self.disks = []

    def flush(self) -> None:
        for d in self.disks:
            d.flush()

    def __enter__(self):
        if not self.disks:
            self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    # ---- 容量调整 ----
    def truncate_bytes(self, size_bytes: int) -> int:
        """卷目前不支持在线扩容（成员盘大小不同，实现复杂）。

        若确实需要扩容，建议新建更大成员盘 + 数据迁移。
        """
        raise VolumeError("Volume 不支持在线扩容")

    # ---- 块级 IO（与 VirtualDisk 兼容） ----
    def read_block(self, logical: int) -> bytes:
        if logical < 0 or logical >= self.nblocks:
            raise ValueError(f"逻辑块越界: {logical} (总块数 {self.nblocks})")
        return self._read_block_raw(logical)

    def write_block(self, logical: int, data: bytes) -> None:
        if logical < 0 or logical >= self.nblocks:
            raise ValueError(f"逻辑块越界: {logical} (总块数 {self.nblocks})")
        self._write_block_raw(logical, data)

    def _read_block_raw(self, logical: int) -> bytes:
        """读取逻辑块，按模式映射到底层盘。

        Volume 的逻辑块号从 0 开始，对应成员盘的块 1（块 0 是卷元数据）。
        因此底层盘的物理块号 = 逻辑块号 + 1。
        """
        assert self.meta is not None
        if self.meta.mode == MODE_CONCAT:
            return self._read_concat(logical)
        elif self.meta.mode == MODE_STRIPE:
            return self._read_stripe(logical)
        elif self.meta.mode == MODE_MIRROR:
            return self._read_mirror(logical)
        raise VolumeError(f"未知模式: {self.meta.mode}")

    def _write_block_raw(self, logical: int, data: bytes) -> None:
        assert self.meta is not None
        if self.meta.mode == MODE_CONCAT:
            self._write_concat(logical, data)
        elif self.meta.mode == MODE_STRIPE:
            self._write_stripe(logical, data)
        elif self.meta.mode == MODE_MIRROR:
            self._write_mirror(logical, data)

    # ---- concat ----
    def _read_concat(self, logical: int) -> bytes:
        for d in self.disks:
            usable = d.nblocks - 1  # 去掉卷元数据块
            if logical < usable:
                return d.read_block(logical + 1)  # +1 跳过元数据块
            logical -= usable
        raise VolumeError("concat 读取越界")

    def _write_concat(self, logical: int, data: bytes) -> None:
        for d in self.disks:
            usable = d.nblocks - 1
            if logical < usable:
                d.write_block(logical + 1, data)
                return
            logical -= usable
        raise VolumeError("concat 写入越界")

    # ---- stripe (RAID0) ----
    def _stripe_locate(self, logical: int) -> Tuple[int, int]:
        """返回 (disk_index, physical_block_in_disk)。"""
        assert self.meta is not None
        stripe_blocks = max(1, self.meta.stripe_size // self.block_size)
        ndisks = len(self.disks)
        round_idx = logical // (stripe_blocks * ndisks)
        in_round = logical % (stripe_blocks * ndisks)
        disk_idx = in_round // stripe_blocks
        block_in_disk = round_idx * stripe_blocks + (in_round % stripe_blocks)
        # +1 跳过成员盘的卷元数据块
        return disk_idx, block_in_disk + 1

    def _read_stripe(self, logical: int) -> bytes:
        disk_idx, blk = self._stripe_locate(logical)
        return self.disks[disk_idx].read_block(blk)

    def _write_stripe(self, logical: int, data: bytes) -> None:
        disk_idx, blk = self._stripe_locate(logical)
        self.disks[disk_idx].write_block(blk, data)

    # ---- mirror (RAID1) ----
    def _read_mirror(self, logical: int) -> bytes:
        last = None
        for i, disk in enumerate(self.disks):
            try:
                data = disk.read_block(logical + 1)
                for h in self._member_health:
                    if os.path.abspath(h["path"]) == os.path.abspath(disk.path):
                        h.update(healthy=True, error=None)
                return data
            except (OSError, RuntimeError, ValueError) as exc:
                last = exc
                for h in self._member_health:
                    if os.path.abspath(h["path"]) == os.path.abspath(disk.path):
                        h.update(healthy=False, error=str(exc))
        raise VolumeError(f"镜像无健康成员: {last}")

    def _write_mirror(self, logical: int, data: bytes) -> None:
        # 写入所有在线成员；单成员失败不影响其他副本。
        for d in self.disks:
            try:
                d.write_block(logical + 1, data)
                for h in self._member_health:
                    if os.path.abspath(h["path"]) == os.path.abspath(d.path):
                        h.update(healthy=True, error=None)
            except (OSError, RuntimeError, ValueError) as exc:
                for h in self._member_health:
                    if os.path.abspath(h["path"]) == os.path.abspath(d.path):
                        h.update(healthy=False, error=str(exc))
        # During create_volume metadata is installed before health is initialized.
        if self._member_health and not any(h.get("healthy") for h in self._member_health):
            raise VolumeError("镜像无健康成员")

    # ---- 字节级 IO（与 VirtualDisk 兼容） ----
    def read_bytes(self, offset: int, length: int) -> bytes:
        """按字节偏移读取 length 字节。

        只读取实际覆盖到的块，按需读取头部/尾部未对齐的部分，避开无谓的整块读。
        """
        if length <= 0:
            return b""
        bs = self.block_size
        end = offset + length  # 区间左闭右开 [offset, end)
        start_block, start_in = divmod(offset, bs)
        # 最后一字节所在的块（包含），不能超过 self.nblocks
        end_block = min((end - 1) // bs, self.nblocks - 1)
        if end_block < start_block:
            # 区间全部落在文件末尾之后，按空洞返回零
            return b"\x00" * length
        # 先读第一个块，按需只取尾部
        first = self.read_block(start_block)
        if start_block == end_block:
            return first[start_in:start_in + length]
        # 中间的整块直接拼接
        chunks = [first[start_in:]]
        if end_block - start_block > 1:
            for blk in range(start_block + 1, end_block):
                chunks.append(self.read_block(blk))
        # 最后一个块按需只取首部
        last = self.read_block(end_block)
        chunks.append(last[: end - end_block * bs])
        return b"".join(chunks)

    def write_bytes(self, offset: int, data: bytes) -> None:
        bs = self.block_size
        start_block = offset // bs
        end_block = (offset + len(data) - 1) // bs
        # 如果只覆盖部分块，需要先读出原数据
        pos = 0
        for blk in range(start_block, end_block + 1):
            block_start = blk * bs
            block_end = block_start + bs
            data_start = offset + pos
            data_end = data_start + (len(data) - pos)
            in_block_start = max(data_start, block_start) - block_start
            in_block_end = min(data_end, block_end) - block_start
            chunk_len = in_block_end - in_block_start
            if in_block_start == 0 and chunk_len == bs:
                # 整块覆盖
                self.write_block(blk, data[pos:pos + bs])
            else:
                # 部分覆盖：读-改-写
                original = bytearray(self.read_block(blk))
                original[in_block_start:in_block_end] = (
                    data[pos:pos + chunk_len]
                )
                self.write_block(blk, bytes(original))
            pos += chunk_len

    # ---- 元数据持久化 ----
    def _write_meta_to_all(self) -> None:
        assert self.meta is not None
        from .identity import DISK_ID_TRAILER_SIZE, make_trailer
        raw = self.meta.to_bytes()
        # 为 block 0 末尾的磁盘身份尾标预留空间
        max_meta = self.block_size - DISK_ID_TRAILER_SIZE
        if len(raw) > max_meta:
            raise VolumeError("卷元数据过大，超出块剩余空间")
        # 公共元数据，补齐到完整块（尾标区先置零，后面逐盘覆盖为自己的 uuid）
        common = raw + b"\x00" * (self.block_size - len(raw))
        for i, d in enumerate(self.disks):
            member = self.meta.members[i]
            block = bytearray(common)
            trailer = make_trailer(member.uuid, self.meta.vol_id,
                                   self.meta.name, is_member=True)
            block[-DISK_ID_TRAILER_SIZE:] = trailer
            d.write_block(VOL_SB_BLOCK, bytes(block))
        self.flush()

    # ---- 状态查询 ----
    def status(self) -> dict:
        assert self.meta is not None
        return {
            "vol_id": self.meta.vol_id,
            "name": self.meta.name,
            "mode": self.meta.mode,
            "stripe_size": self.meta.stripe_size,
            "block_size": self.block_size,
            "total_blocks": self.meta.total_blocks,
            "data_blocks": self.meta.data_blocks,
            "total_bytes": self.meta.total_blocks * self.block_size,
            "ndisks": len(self.disks),
            "health": "healthy" if all(x.get("healthy", True) for x in self._member_health) else "degraded",
            "degraded": any(not x.get("healthy", True) for x in self._member_health),
            "member_health": list(self._member_health),
            "members": [
                {"path": m.path, "blocks": m.blocks, "uuid": m.uuid}
                for m in self.meta.members
            ],
            "mode_desc": {
                MODE_CONCAT: "级联（容量叠加）",
                MODE_STRIPE: "条带 RAID0（并行）",
                MODE_MIRROR: "镜像 RAID1（冗余）",
            }.get(self.meta.mode, self.meta.mode),
        }


# ---- 卷创建 / 管理 ----
def create_volume(paths: List[str], mode: str, name: str = "",
                  stripe_size: int = DEFAULT_STRIPE_SIZE,
                  block_size: int = DEFAULT_BLOCK_SIZE,
                  disk_size: Optional[int] = None) -> Volume:
    """创建一个多盘卷。

    paths: 成员盘路径列表
    mode: concat / stripe / mirror
    disk_size: 若指定且盘文件不存在，则按此大小创建空盘
    """
    from .identity import validate_disk_path
    for path in paths:
        validate_disk_path(path)
    if mode not in VALID_MODES:
        raise VolumeError(f"未知模式: {mode}，支持: {VALID_MODES}")
    if len(paths) < 1:
        raise VolumeError("至少需要一块盘")
    if mode in (MODE_STRIPE, MODE_MIRROR) and len(paths) < 2:
        raise VolumeError(f"{mode} 模式至少需要 2 块盘")

    # 创建或打开成员盘
    disks: List[VirtualDisk] = []
    members: List[DiskMember] = []
    try:
        for p in paths:
            if not os.path.exists(p):
                if disk_size is None:
                    raise VolumeError(f"盘文件不存在且未指定 disk_size: {p}")
                d = VirtualDisk(p, block_size)
                d.create(disk_size)
                d.open()
            else:
                d = VirtualDisk(p, block_size)
                d.open()
            disks.append(d)
            members.append(DiskMember(
                path=p,
                blocks=d.nblocks,
                uuid=str(uuid.uuid4()),
            ))
        # 计算几何
        total_blocks, data_blocks = Volume.compute_geometry(
            mode, [m.blocks for m in members], stripe_size, block_size
        )
        vol_id = str(uuid.uuid4())
        meta = VolumeMeta(
            vol_id=vol_id,
            name=name or f"vol-{vol_id[:8]}",
            mode=mode,
            stripe_size=stripe_size,
            block_size=block_size,
            members=members,
            created=int(time.time()),
            total_blocks=total_blocks,
            data_blocks=data_blocks,
        )
        # 写元数据到所有盘
        vol = Volume(block_size=block_size)
        vol.disks = disks
        vol.meta = meta
        vol.nblocks = total_blocks
        vol._write_meta_to_all()
        return vol
    except Exception:
        for d in disks:
            try:
                d.close()
            except Exception:
                pass
        raise


def open_volume(paths: List[str], block_size: int = DEFAULT_BLOCK_SIZE) -> Volume:
    """打开一个已存在的卷。paths 顺序必须与创建时一致。"""
    vol = Volume(paths, block_size=block_size)
    vol.open()
    return vol


def add_mirror(paths: List[str], new_disk_path: str,
               new_disk_size: Optional[int] = None,
               block_size: int = DEFAULT_BLOCK_SIZE) -> Volume:
    """向镜像卷添加一块盘（从主盘复制数据）。

    仅适用于 mirror 模式。
    """
    vol = open_volume(paths, block_size)
    try:
        assert vol.meta is not None
        if vol.meta.mode != MODE_MIRROR:
            raise VolumeError("只能向镜像卷添加盘")
        # 确定新盘大小：至少等于当前主盘大小
        primary = vol.disks[0]
        needed_blocks = primary.nblocks
        needed_size = needed_blocks * block_size
        if new_disk_size is not None and new_disk_size < needed_size:
            raise VolumeError(
                f"新盘太小：需要至少 {needed_size} 字节，指定 {new_disk_size}"
            )
        actual_size = new_disk_size if new_disk_size else needed_size
        # 创建新盘
        new_disk = VirtualDisk(new_disk_path, block_size)
        new_disk.create(actual_size)
        new_disk.open()
        # 从主盘复制所有数据块（含卷超级块）
        for blk in range(needed_blocks):
            data = primary.read_block(blk)
            new_disk.write_block(blk, data)
        new_disk.flush()
        # 更新元数据
        vol.disks.append(new_disk)
        vol.meta.members.append(DiskMember(
            path=new_disk_path,
            blocks=new_disk.nblocks,
            uuid=str(uuid.uuid4()),
        ))
        vol._write_meta_to_all()
        return vol
    finally:
        vol.close()


def remove_mirror(paths: List[str], remove_path: str,
                  block_size: int = DEFAULT_BLOCK_SIZE) -> Volume:
    """从镜像卷移除一块盘（保留至少一块）。

    仅适用于 mirror 模式。
    """
    vol = open_volume(paths, block_size)
    try:
        assert vol.meta is not None
        if vol.meta.mode != MODE_MIRROR:
            raise VolumeError("只能从镜像卷移除盘")
        if len(vol.disks) <= 2:
            raise VolumeError("镜像卷至少保留 2 块盘")
        # 找到要移除的盘
        idx = None
        for i, d in enumerate(vol.disks):
            if os.path.abspath(d.path) == os.path.abspath(remove_path):
                idx = i
                break
        if idx is None:
            raise VolumeError(f"盘不在卷中: {remove_path}")
        removed = vol.disks.pop(idx)
        vol.meta.members = [
            m for m in vol.meta.members
            if os.path.abspath(m.path) != os.path.abspath(remove_path)
        ]
        vol._write_meta_to_all()
        removed.close()
        return vol
    finally:
        vol.close()


def resync_mirror(paths: List[str], block_size: int = DEFAULT_BLOCK_SIZE) -> Volume:
    """重新同步镜像卷：以第一块盘为基准，复制到所有其他盘。

    用于某块盘数据不一致或刚替换后修复。
    """
    vol = open_volume(paths, block_size)
    try:
        assert vol.meta is not None
        if vol.meta.mode != MODE_MIRROR:
            raise VolumeError("只能重新同步镜像卷")
        primary = vol.disks[0]
        for d in vol.disks[1:]:
            # 同步所有块（含卷超级块）
            n = min(primary.nblocks, d.nblocks)
            for blk in range(n):
                data = primary.read_block(blk)
                d.write_block(blk, data)
            d.flush()
        return vol
    finally:
        vol.close()
