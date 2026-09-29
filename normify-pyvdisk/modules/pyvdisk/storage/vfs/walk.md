---
uid: a000050c
id: pyvdisk.storage.vfs.walk
parent: pyvdisk.storage.vfs
name: {zh: "目录遍历", en: "Directory Walk"}
description:
  zh: >
      递归目录遍历生成器，供 import_host_tree、du 与 CLI 树视图使用。
  en: >
      Recursive directory traversal generator, used by import_host_tree, du and the CLI tree view.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 437
    end_line: 457
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#walk"
    description:
      zh: >
          自某目录起递归产出 (path, dirnames, filenames) 三元组。
      en: >
          Recursively yield (path, dirnames, filenames) triples rooted at a directory.
---
