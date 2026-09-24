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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.225Z"
fingerprint: 3ed800d0914e362e6fa76cf02ccddaa8b41f54ffd8efabaebe018e25619b823f
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
