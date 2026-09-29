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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.252Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
