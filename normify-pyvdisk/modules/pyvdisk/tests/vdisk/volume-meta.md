---
uid: a0000d0c
id: pyvdisk.tests.vdisk.volume-meta
parent: pyvdisk.tests.vdisk
name: {zh: "卷元数据用例", en: "Volume Metadata Tests"}
description:
  zh: >
      卷元数据与错误处理，以及卷 CLI 接口。
  en: >
      Volume metadata and error handling plus the volume CLI surface.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 851
    end_line: 948
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeMeta"
    description:
      zh: >
          卷元数据、成员记录与几何持久化。
      en: >
          Volume metadata, member records and geometry persistence.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeErrors"
    description:
      zh: >
          成员缺失、重复或不匹配的错误用例。
      en: >
          Error cases for missing, duplicated or mismatched members.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeCLI"
    description:
      zh: >
          卷 CLI 子命令接口。
      en: >
          Volume CLI subcommand surface.
---
