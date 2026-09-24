---
uid: a0000506
id: pyvdisk.storage.vfs.dirs
parent: pyvdisk.storage.vfs
name: {zh: "目录创建", en: "Directory Creation"}
description:
  zh: >
      目录创建辅助，含用于命名空间初始化的递归变体。
  en: >
      Directory creation helpers, including the recursive variant used for namespace setup.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 248
    end_line: 263
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#mkdir"
    description:
      zh: >
          创建单个目录。
      en: >
          Create one directory.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#makedirs"
    description:
      zh: >
          递归创建目录树，忽略已存在的层。
      en: >
          Create a directory tree, ignoring existing components.
---
