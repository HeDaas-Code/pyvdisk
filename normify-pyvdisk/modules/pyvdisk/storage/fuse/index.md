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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 5fe2c5a2cde43ccd63a7a2c90ca4f237f91e4c1de74900e83ebc49d9e6dc5193
source:
  - path: "pyvdisk/fuse_mount.py"
---
