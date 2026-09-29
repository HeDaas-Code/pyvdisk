---
uid: a0000a08
id: pyvdisk.vscript.policy.capability
parent: pyvdisk.vscript.policy
name: {zh: "脚本能力", en: "Script Capability"}
description:
  zh: >
      脚本可见的能力对象及其权限门禁。
  en: >
      The script-visible capability object and its permission gate.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: ff47ac976336485cb37963fa8268f69553eddc1f28f20df0efb89166391276a6
source:
  - path: "pyvdisk/vscript/policy.py"
    line: 38
    end_line: 46
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Capability"
    description:
      zh: >
          已授权句柄及脚本可经其使用的权限集。
      en: >
          A granted handle plus the permission set a script may use through it.
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Capability#require"
    description:
      zh: >
          缺少任一权限时抛出能力错误。
      en: >
          Raise a capability error unless every listed permission is granted.
---
