---
uid: a0000508
id: pyvdisk.storage.vfs.remove
parent: pyvdisk.storage.vfs
name: {zh: "删除与重命名", en: "Delete and Rename"}
description:
  zh: >
      删除与重命名操作，含检查点清理使用的递归目录删除。
  en: >
      Deletion and rename operations, including the recursive tree removal used by checkpoint cleanup.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 304
    end_line: 337
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#remove"
    description:
      zh: >
          删除文件。
      en: >
          Remove a file.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#rmdir"
    description:
      zh: >
          删除空目录。
      en: >
          Remove an empty directory.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#rmtree"
    description:
      zh: >
          递归删除目录树。
      en: >
          Recursively remove a directory tree.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#rename"
    description:
      zh: >
          重命名或移动路径。
      en: >
          Rename or move a path.
---
