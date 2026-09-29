---
uid: a000030c
id: pyvdisk.storage.fuse
parent: pyvdisk.storage
tags: [fuse, optional]
name: {zh: "FUSE 挂载", en: "FUSE Mount"}
description:
  zh: >
      可选 FUSE 挂载：把 VFS 暴露为宿主目录；缺少 fusepy 时给出清晰的 ImportError。
      
  en: >
      Optional FUSE mount that exposes a VFS as a host directory; degrades to a clear ImportError when fusepy is absent.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: c711d0ed315e831e5d1d2873c7557dc5e72c8dcb01ee91556eb39cb3065c5d76
source:
  - path: "pyvdisk/fuse_mount.py"
---
