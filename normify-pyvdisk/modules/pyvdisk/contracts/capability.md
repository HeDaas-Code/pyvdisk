---
uid: a000010d
id: pyvdisk.contracts.capability
parent: pyvdisk.contracts
name: {zh: "能力授权", en: "Capability Grant"}
description:
  zh: >
      Capability 枚举与 CapabilityGrant：治理层、执行上下文与 VScript 共用的权限词表。
  en: >
      Capability enum and CapabilityGrant: the permission vocabulary shared by governance, execution contexts and VScript.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 16
    end_line: 37
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.Capability"
    description:
      zh: >
          能力权限枚举：read、write、append、admin。
      en: >
          Capability permission enum: read, write, append, admin.
  - protocol: rpc
    path: "pyvdisk.contracts.CapabilityGrant"
    description:
      zh: >
          单次执行持有的具名、可限定范围的授权。
      en: >
          Named, optionally scoped grant held by one execution.
  - protocol: rpc
    path: "pyvdisk.contracts.CapabilityGrant#allows"
    description:
      zh: >
          判断某权限在给定范围下是否被允许。
      en: >
          Check whether a permission is allowed inside an optional scope.
  - protocol: rpc
    path: "pyvdisk.contracts.CapabilityGrant#require"
    description:
      zh: >
          缺少任一权限时抛出 PermissionError。
      en: >
          Raise PermissionError unless every listed permission is granted.
---
