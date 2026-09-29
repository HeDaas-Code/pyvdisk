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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.244Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
