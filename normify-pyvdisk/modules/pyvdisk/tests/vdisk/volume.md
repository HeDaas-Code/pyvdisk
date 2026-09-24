---
uid: a0000d0a
id: pyvdisk.tests.vdisk.volume
parent: pyvdisk.tests.vdisk
name: {zh: "卷模式用例", en: "Volume Mode Tests"}
description:
  zh: >
      拼接与条带两种无冗余模式的卷用例。
      
  en: >
      Volume mode tests for concatenation and striping, the two modes without redundancy.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.251Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
source:
  - path: "tests/test_vdisk.py"
    line: 682
    end_line: 781
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeBase"
    description:
      zh: >
          构建成员镜像的共享卷夹具。
          
      en: >
          Shared volume fixture building member images.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeConcat"
    description:
      zh: >
          跨多个成员的拼接卷。
          
      en: >
          Concatenation volume spanning multiple members.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVolumeStripe"
    description:
      zh: >
          条带卷的分布与读回。
          
      en: >
          Striped volume distribution and read-back.
          
---
