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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.253Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
