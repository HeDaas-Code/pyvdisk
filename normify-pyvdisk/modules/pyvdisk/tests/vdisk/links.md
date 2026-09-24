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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
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
