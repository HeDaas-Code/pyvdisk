---
uid: a0000d06
id: pyvdisk.tests.vdisk.maintenance
parent: pyvdisk.tests.vdisk
name: {zh: "维护用例", en: "Maintenance Tests"}
description:
  zh: >
      维护类用例：一致性检查、就地扩容与空间统计。
      
  en: >
      Maintenance tests: consistency checking, in-place growth and space accounting.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.248Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
source:
  - path: "tests/test_vdisk.py"
    line: 421
    end_line: 511
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestFsck"
    description:
      zh: >
          对注入的元数据损坏进行 fsck 检测与修复。
          
      en: >
          fsck detection and repair of injected metadata damage.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestGrow"
    description:
      zh: >
          就地镜像扩容与后续分配。
          
      en: >
          In-place image growth and continued allocation.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestSpaceInfo"
    description:
      zh: >
          df 与 du 空间统计。
          
      en: >
          df and du space accounting.
          
---
