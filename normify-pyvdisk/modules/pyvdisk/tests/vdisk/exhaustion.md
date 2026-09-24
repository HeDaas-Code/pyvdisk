---
uid: a0000d09
id: pyvdisk.tests.vdisk.exhaustion
parent: pyvdisk.tests.vdisk
name: {zh: "空间耗尽用例", en: "Space Exhaustion Tests"}
description:
  zh: >
      空间耗尽行为：分配失败必须上报，不得静默损坏。
  en: >
      Space exhaustion behaviour, where allocation failure must be reported rather than silently corrupting.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 671
    end_line: 681
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestSpaceExhaustion"
    description:
      zh: >
          镜像写满时的行为：暴露 ENOSPC 而不损坏元数据。
      en: >
          Behaviour when the image is full: ENOSPC surfaces instead of corrupting metadata.
---
