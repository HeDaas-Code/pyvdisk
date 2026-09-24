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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
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
