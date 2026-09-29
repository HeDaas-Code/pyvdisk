---
uid: a0000d02
id: pyvdisk.tests.vdisk.large-files
parent: pyvdisk.tests.vdisk
name: {zh: "大文件与删除用例", en: "Large File and Remove Tests"}
description:
  zh: >
      间接块与目录删除行为，即块记账与 inode 复用最易出错的两处。
      
  en: >
      Indirect-block and directory-removal behaviour, the two places where block accounting and inode reuse most often break.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.245Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
source:
  - path: "tests/test_vdisk.py"
    line: 79
    end_line: 151
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestLargeFiles"
    description:
      zh: >
          单/双间接块映射、部分读写与截断扩缩。
          
      en: >
          Single and double indirect block mapping, partial IO and truncate grow/shrink.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestDirsAndRemove"
    description:
      zh: >
          文件删除、rmdir 语义与深度递归 rmtree。
          
      en: >
          File removal, rmdir semantics and deep recursive rmtree.
          
---
