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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.231Z"
fingerprint: b4475de0aa022f77959dd296d825fe99caca40036a8a86be29dcd1e6d6c0cf47
source:
  - path: "pyvdisk/fuse_mount.py"
---
