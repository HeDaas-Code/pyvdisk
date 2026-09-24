---
uid: a0000d07
id: pyvdisk.tests.vdisk.raw-fs
parent: pyvdisk.tests.vdisk
name: {zh: "裸文件系统用例", en: "Raw Filesystem Tests"}
description:
  zh: >
      直接操作块设备与磁盘布局、绕过 VFS 门面的用例。
      
  en: >
      Tests that exercise the block device and on-disk layout directly, bypassing the VFS facade.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.249Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
source:
  - path: "tests/test_vdisk.py"
    line: 512
    end_line: 535
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestRawFS"
    description:
      zh: >
          绕过 VFS 的裸块设备级读写。
          
      en: >
          Raw block-device level reads and writes outside the VFS.
          
---
