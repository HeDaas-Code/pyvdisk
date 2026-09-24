---
uid: a0000d0b
id: pyvdisk.tests.vdisk.volume-mirror
parent: pyvdisk.tests.vdisk
name: {zh: "镜像卷用例", en: "Mirror Volume Tests"}
description:
  zh: >
      镜像模式用例：区别于拼接与条带的冗余契约。
  en: >
      Mirror-mode tests: the redundancy contract that distinguishes it from concat and stripe.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 782
    end_line: 850
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeMirror"
    description:
      zh: >
          镜像卷冗余、成员丢失与重新同步。
      en: >
          Mirror volume redundancy, member loss and resync.
---
