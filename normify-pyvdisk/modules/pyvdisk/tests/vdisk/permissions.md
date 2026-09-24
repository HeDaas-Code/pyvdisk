---
uid: a0000d11
id: pyvdisk.tests.vdisk.permissions
parent: pyvdisk.tests.vdisk
name: {zh: "权限用例", en: "Permission Tests"}
description:
  zh: >
      权限用例：跨 uid 与 gid 组合遵守读、写、执行位。
  en: >
      Permission tests: read, write and execute bits honoured across uid and gid combinations.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 1419
    end_line: 1536
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestPermissions"
    description:
      zh: >
          模式、属主与 root 旁路的权限强制。
      en: >
          Permission enforcement for mode, owner and root bypass.
---
