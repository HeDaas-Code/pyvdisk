---
uid: a0000d0a
id: pyvdisk.tests.vdisk.volume
parent: pyvdisk.tests.vdisk
name: {zh: "卷模式用例", en: "Volume Mode Tests"}
description:
  zh: >
      拼接与条带两种无冗余模式的卷用例。
  en: >
      Volume mode tests for concatenation and striping, the two modes without redundancy.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 682
    end_line: 781
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeBase"
    description:
      zh: >
          构建成员镜像的共享卷夹具。
      en: >
          Shared volume fixture building member images.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeConcat"
    description:
      zh: >
          跨多个成员的拼接卷。
      en: >
          Concatenation volume spanning multiple members.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeStripe"
    description:
      zh: >
          条带卷的分布与读回。
      en: >
          Striped volume distribution and read-back.
---
