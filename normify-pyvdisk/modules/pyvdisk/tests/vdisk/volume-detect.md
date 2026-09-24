---
uid: a0000d0d
id: pyvdisk.tests.vdisk.volume-detect
parent: pyvdisk.tests.vdisk
name: {zh: "卷检测用例", en: "Volume Detection Tests"}
description:
  zh: >
      从设备内容而非配置自动检测卷成员关系。
  en: >
      Automatic detection of volume membership from device contents, not configuration.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 949
    end_line: 1006
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeAutoDetect"
    description:
      zh: >
          基于扫描的卷自动检测与挂载。
      en: >
          Scan-based automatic volume detection and mounting.
---
