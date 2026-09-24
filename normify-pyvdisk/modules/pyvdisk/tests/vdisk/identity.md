---
uid: a0000d0e
id: pyvdisk.tests.vdisk.identity
parent: pyvdisk.tests.vdisk
name: {zh: "身份用例", en: "Identity Tests"}
description:
  zh: >
      身份用例：让宿主文件可被识别为 pyvdisk 镜像的尾标。
  en: >
      Identity tests: the trailer that lets a host file be recognised as a pyvdisk image.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 1007
    end_line: 1072
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestIdentity"
    description:
      zh: >
          身份尾标生成、校验与损坏拒绝。
      en: >
          Identity trailer generation, validation and corruption rejection.
---
