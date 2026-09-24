"""模拟磁盘驱动器 / 虚拟磁盘管理器。

把一个宿主目录当成"硬盘柜"：目录下的每个 *.vdisk 文件就是一块"硬盘"。
驱动器扫描目录，读取每块盘的身份尾标（VDID），识别出：

    - 单盘文件系统（VDK1）：直接可挂载
    - 多盘卷成员盘（VDV1）：按 vol_id 聚合，所有成员盘到齐后组装成完整卷

识别 / 组装完全基于盘自带的统一识别码（disk_uuid / vol_id），**不依赖文件
路径**——把 .vdisk 文件复制 / 移动到目录里就能被识别并尝试挂载，模拟真实硬盘
的热插拔。

挂载后按"卷标"（label）统一索引：单盘用其尾标里的 label，卷用卷名。
可通过 `manager.get(label)` 拿到对应的 VFS。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .disk import DEFAULT_BLOCK_SIZE
from .identity import DiskIdentity, probe_disk
from .volume import VolumeMeta, open_volume
from .vfs import VFS


@dataclass
class AssembledVolume:
    """一个被驱动器组装中的多盘卷。"""
    vol_id: str
    meta: VolumeMeta
    members: Dict[str, DiskIdentity] = field(default_factory=dict)  # uuid -> identity

    @property
    def complete(self) -> bool:
        """所有成员盘都已就位。"""
        return all(m.uuid in self.members for m in self.meta.members)

    @property
    def found(self) -> int:
        return len(self.members)

    @property
    def needed(self) -> int:
        return len(self.meta.members)

    def ordered_paths(self) -> List[str]:
        """按 meta.members 顺序返回成员盘路径。"""
        return [self.members[m.uuid].path for m in self.meta.members
                if m.uuid in self.members]


@dataclass
class MountedLog:
    """一个已挂载的日志数据盘。"""
    label: str
    kind: str
    uuid: str
    store: "LogDisk"
    paths: List[str]

    @property
    def vfs(self):
        return self.store.vfs

    def close(self):
        self.store.close()


@dataclass
class MountedVector:
    """一个已挂载的向量数据盘。"""
    label: str
    kind: str
    uuid: str
    store: "VectorDisk"
    paths: List[str]

    def close(self):
        self.store.close()


@dataclass
class MountedFS:
    """一个已挂载的文件系统（单盘或卷），按卷标索引。"""
    label: str
    kind: str                     # "single" | "volume"
    uuid: str                     # 单盘=disk_uuid，卷=vol_id
    vfs: VFS
    paths: List[str]              # 底层盘路径
    members: Optional[List[DiskIdentity]] = None  # 卷的成员身份清单

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.vfs.close()


class DiskManager:
    """模拟磁盘驱动器：扫描目录 → 识别盘 → 组装卷 → 按卷标挂载。

    用法：
        mgr = DiskManager("/tmp/drivebay")
        mgr.scan()              # 识别所有盘
        mgr.mount_all()         # 挂载所有可挂载的盘/卷
        vfs = mgr.get("myvol").vfs   # 按卷标访问
        mgr.hotplug()           # 复制新盘进目录后重新扫描挂载
    """

    def __init__(self, host_dir: str, block_size: int = DEFAULT_BLOCK_SIZE):
        self.host_dir = host_dir
        self.block_size = block_size
        # disk_uuid -> DiskIdentity
        self.identities: Dict[str, DiskIdentity] = {}
        # vol_id -> AssembledVolume
        self.assembled: Dict[str, AssembledVolume] = {}
        # label -> MountedFS
        self.mounted: Dict[str, MountedFS] = {}
        self._used_labels: set = set()

    # ---- 扫描 ----
    def scan(self) -> List[DiskIdentity]:
        """扫描 host_dir 下的 *.vdisk 文件，探测每块盘的身份。"""
        self.identities.clear()
        if not os.path.isdir(self.host_dir):
            return []
        for fn in sorted(os.listdir(self.host_dir)):
            if not fn.lower().endswith(".vdisk"):
                continue
            p = os.path.join(self.host_dir, fn)
            if not os.path.isfile(p):
                continue
            ident = probe_disk(p, self.block_size)
            if ident.kind == "unknown":
                continue
            key = ident.disk_uuid or p
            self.identities[key] = ident
        return list(self.identities.values())

    # ---- 组装 ----
    def assemble(self) -> Tuple[List[DiskIdentity], List[AssembledVolume],
                                 List[AssembledVolume]]:
        """按 vol_id 组装卷。

        返回 (单盘清单, 完整卷清单, 不完整卷清单)。
        """
        self.assembled.clear()
        singles: List[DiskIdentity] = []
        for ident in self.identities.values():
            if ident.is_complete_member and ident.vol_meta is not None:
                vol_id = ident.vol_id
                if vol_id not in self.assembled:
                    self.assembled[vol_id] = AssembledVolume(
                        vol_id=vol_id, meta=ident.vol_meta
                    )
                av = self.assembled[vol_id]
                if ident.disk_uuid in {m.uuid for m in av.meta.members}:
                    av.members[ident.disk_uuid] = ident
            elif ident.is_single:
                singles.append(ident)
        complete = [av for av in self.assembled.values() if av.complete]
        partial = [av for av in self.assembled.values() if not av.complete]
        return singles, complete, partial

    # ---- 挂载 ----
    def _unique_label(self, label: str) -> str:
        if not label:
            label = "unlabeled"
        base = label
        i = 2
        while label in self._used_labels:
            label = f"{base}-{i}"
            i += 1
        self._used_labels.add(label)
        return label

    def _mount_single(self, ident: DiskIdentity) -> Optional[MountedFS]:
        try:
            vfs = VFS(ident.path, self.block_size)
            vfs.mount()
        except Exception:
            return None
        label = self._unique_label(ident.label or f"disk-{ident.disk_uuid[:8]}")
        m = MountedFS(label=label, kind="single", uuid=ident.disk_uuid,
                      vfs=vfs, paths=[ident.path])
        self.mounted[label] = m
        return m

    def _mount_vector(self, ident: DiskIdentity) -> Optional[MountedVector]:
        from .vector_disk import VectorDisk
        try:
            store = VectorDisk(ident.path).mount()
        except Exception:
            return None
        label = self._unique_label(ident.label or f"vector-{ident.disk_uuid[:8]}")
        mounted = MountedVector(label=label, kind="vector", uuid=ident.disk_uuid,
                                store=store, paths=[ident.path])
        self.mounted[label] = mounted
        return mounted

    def _mount_log(self, ident: DiskIdentity) -> Optional[MountedLog]:
        from .log_disk import LogDisk
        try:
            store = LogDisk(ident.path).mount()
        except Exception:
            return None
        label = self._unique_label(ident.label or f"log-{ident.disk_uuid[:8]}")
        mounted = MountedLog(label=label, kind="log", uuid=ident.disk_uuid,
                             store=store, paths=[ident.path])
        self.mounted[label] = mounted
        return mounted

    def _mount_volume(self, av: AssembledVolume) -> Optional[MountedFS]:
        paths = av.ordered_paths()
        if len(paths) != av.needed:
            return None
        try:
            vol = open_volume(paths, self.block_size)
            vfs = VFS(vol, self.block_size)
            vfs.mount()
        except Exception:
            return None
        label = self._unique_label(av.meta.name or f"vol-{av.vol_id[:8]}")
        m = MountedFS(label=label, kind="volume", uuid=av.vol_id,
                      vfs=vfs, paths=paths,
                      members=[av.members[mm.uuid] for mm in av.meta.members])
        self.mounted[label] = m
        return m

    def mount_all(self) -> Dict[str, MountedFS]:
        """挂载所有单盘和完整卷，按卷标注册。"""
        # 保留已挂载的，只挂新的
        singles, complete, _partial = self.assemble()
        vectors = [i for i in self.identities.values() if i.is_vector]
        logs = [i for i in self.identities.values() if i.is_log]
        for ident in singles:
            key = ident.disk_uuid
            if not any(m.kind == "single" and m.uuid == key
                       for m in self.mounted.values()):
                self._mount_single(ident)
        for ident in vectors:
            if not any(m.kind == "vector" and m.uuid == ident.disk_uuid
                       for m in self.mounted.values()):
                self._mount_vector(ident)
        for ident in logs:
            if not any(m.kind == "log" and m.uuid == ident.disk_uuid
                       for m in self.mounted.values()):
                self._mount_log(ident)
        for av in complete:
            if not any(m.kind == "volume" and m.uuid == av.vol_id
                       for m in self.mounted.values()):
                self._mount_volume(av)
        return dict(self.mounted)

    # ---- 访问 ----
    def get(self, label: str) -> MountedFS:
        return self.mounted[label]

    def labels(self) -> List[str]:
        return list(self.mounted.keys())

    def unmount(self, label: str) -> None:
        m = self.mounted.pop(label, None)
        if m is None:
            raise KeyError(f"没有该卷标: {label}")
        if m.kind in ("vector", "log"):
            m.store.close()
        else:
            m.vfs.close()
        self._used_labels.discard(label)

    def unmount_all(self) -> None:
        for m in list(self.mounted.values()):
            if m.kind == "vector":
                m.store.close()
            else:
                m.vfs.close()
        self.mounted.clear()
        self._used_labels.clear()

    # ---- 热插拔 ----
    def hotplug(self) -> List[MountedFS]:
        """重新扫描并挂载新增的盘/卷（模拟热插拔）。

        返回本次新挂载的 MountedFS 列表。
        """
        before = set(self.identities.keys())
        self.scan()
        new_keys = [k for k in self.identities if k not in before]
        if not new_keys:
            return []
        # 记录挂载前已有的卷标
        old_labels = set(self.mounted.keys())
        self.mount_all()
        return [self.mounted[l] for l in self.mounted if l not in old_labels]

    # ---- 概览 ----
    def summary(self) -> dict:
        singles, complete, partial = self.assemble()
        return {
            "host_dir": self.host_dir,
            "disks_found": len(self.identities),
            "singles": [
                {"label": i.label, "uuid": i.disk_uuid, "path": i.path,
                 "nblocks": i.nblocks}
                for i in singles
            ],
            "complete_volumes": [
                {"vol_id": av.vol_id, "name": av.meta.name,
                 "mode": av.meta.mode, "members": av.needed, "paths": av.ordered_paths()}
                for av in complete
            ],
            "partial_volumes": [
                {"vol_id": av.vol_id, "name": av.meta.name,
                 "mode": av.meta.mode, "found": av.found, "needed": av.needed}
                for av in partial
            ],
            "mounted": [
                {"label": m.label, "kind": m.kind, "uuid": m.uuid,
                 "paths": m.paths}
                for m in self.mounted.values()
            ],
        }
