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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.249Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
