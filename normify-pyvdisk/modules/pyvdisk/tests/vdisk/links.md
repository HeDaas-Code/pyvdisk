---
uid: a0000d05
id: pyvdisk.tests.vdisk.links
parent: pyvdisk.tests.vdisk
name: {zh: "链接与属性用例", en: "Link and Attribute Tests"}
description:
  zh: >
      inode 层行为：硬链接、属性修改与稀疏分配。
      
  en: >
      Inode-level behaviour: hard links, attribute mutations and sparse allocation.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.246Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
source:
  - path: "tests/test_vdisk.py"
    line: 320
    end_line: 420
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestHardLinks"
    description:
      zh: >
          硬链接创建、引用计数与共享内容行为。
          
      en: >
          Hard link creation, refcount and shared-content behaviour.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestAttributes"
    description:
      zh: >
          模式、uid、gid 与时间戳属性处理。
          
      en: >
          Mode, uid, gid and timestamp attribute handling.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestSparseFile"
    description:
      zh: >
          稀疏文件空洞与表观大小对比实占大小。
          
      en: >
          Sparse file holes and apparent versus allocated size.
          
---
