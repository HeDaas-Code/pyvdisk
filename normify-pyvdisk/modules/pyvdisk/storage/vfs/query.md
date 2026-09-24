---
uid: a0000505
id: pyvdisk.storage.vfs.query
parent: pyvdisk.storage.vfs
name: {zh: "VFS 查询", en: "VFS Queries"}
description:
  zh: >
      VFS 门面上的存在性、类型判定与目录列举。
  en: >
      Existence, type predicates and directory listing on the VFS facade.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 204
    end_line: 246
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#exists"
    description:
      zh: >
          路径存在时为真。
      en: >
          True when the path exists.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#isfile"
    description:
      zh: >
          路径为普通文件时为真。
      en: >
          True when the path is a regular file.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#isdir"
    description:
      zh: >
          路径为目录时为真。
      en: >
          True when the path is a directory.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#listdir"
    description:
      zh: >
          列出目录中的名字。
      en: >
          List the names in a directory.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#listdir_with_stat"
    description:
      zh: >
          列出目录项及其 Stat 对象。
      en: >
          List directory entries together with their Stat objects.
---
