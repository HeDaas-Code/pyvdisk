---
uid: a0000301
id: pyvdisk.storage
parent: pyvdisk
tags: [storage]
name: {zh: "存储平面", en: "Storage Plane"}
description:
  zh: >
      存储平面：块镜像、磁盘身份、盘上文件系统、高层 VFS、多盘卷、向量盘与日志盘、结构化日志、模拟驱动器、可选 FUSE 挂载、统一 DataDisk 容器、WAL 与检查点。
  en: >
      Storage plane: block image, disk identity, on-disk filesystem, high-level VFS, multi-disk volumes, vector and log disks, structured logging, simulated drive bay, optional FUSE mount, the unified DataDisk container, WAL and checkpoints.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 436be34d0da90cb6f3278a96c3f7ec70da5b59a549e92a9ca704acad9bd6ffdb
source:
  - path: "pyvdisk/disk.py"
  - path: "pyvdisk/identity.py"
  - path: "pyvdisk/rwlock.py"
  - path: "pyvdisk/fs.py"
  - path: "pyvdisk/vfs.py"
  - path: "pyvdisk/volume.py"
  - path: "pyvdisk/vector_disk.py"
  - path: "pyvdisk/log_disk.py"
  - path: "pyvdisk/logging_core.py"
  - path: "pyvdisk/driver.py"
  - path: "pyvdisk/fuse_mount.py"
  - path: "pyvdisk/infrastructure/disk.py"
  - path: "pyvdisk/infrastructure/wal.py"
  - path: "pyvdisk/infrastructure/checkpoint.py"
---
