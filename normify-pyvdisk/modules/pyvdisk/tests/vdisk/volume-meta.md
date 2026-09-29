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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.252Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
