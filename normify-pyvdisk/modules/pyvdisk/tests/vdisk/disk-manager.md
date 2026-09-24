---
uid: a0000d0f
id: pyvdisk.tests.vdisk.disk-manager
parent: pyvdisk.tests.vdisk
name: {zh: "磁盘管理用例", en: "Disk Manager Tests"}
description:
  zh: >
      驱动层用例：挂载记账与已挂载文件系统的管理接口。
  en: >
      Driver-level tests: mount bookkeeping and the management surface around mounted filesystems.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 1073
    end_line: 1208
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestDiskManager"
    description:
      zh: >
          DiskManager 的挂载、卸载、列举与卷组装行为。
      en: >
          DiskManager mount, unmount, listing and volume assembly behaviour.
---
