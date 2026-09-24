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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
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
