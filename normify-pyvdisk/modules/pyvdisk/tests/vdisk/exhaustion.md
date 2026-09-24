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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.244Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
