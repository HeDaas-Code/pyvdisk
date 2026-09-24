---
uid: a000080e
id: pyvdisk.governance.namespace
parent: pyvdisk.governance
name: {zh: "能力门禁", en: "Capability Gate"}
description:
  zh: >
      能力门禁：路径归一、范围包含判定，以及所有受限命名空间共用的受保护委托辅助。
      
  en: >
      The capability gate: path normalization, scope containment and the guarded delegation helper all scoped namespaces share.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.308Z"
fingerprint: 799d79402415a8648a6a253e7d9d33664cfd27b7cb5f751693abb7efd6c3cb64
source:
  - path: "pyvdisk/infrastructure/capabilities.py"
    line: 7
    end_line: 49
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities._path"
    description:
      zh: >
          把能力范围归一到以 / 为根、以斜线为界的路径。
          
      en: >
          Normalize a capability scope into a rooted, slash-bounded path.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities._inside"
    description:
      zh: >
          路径被包含在范围内时为真。
          
      en: >
          True when a path is contained in a scope.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.CapabilityNamespace"
    description:
      zh: >
          基础适配器：在委托前把能力检查变为守卫条件。
          
      en: >
          Base adapter that turns capability checks into guard clauses before delegating.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.CapabilityNamespace#_check"
    description:
      zh: >
          对照执行上下文范围检查单个权限。
          
      en: >
          Check one permission against the execution context scope.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.CapabilityNamespace#_call"
    description:
      zh: >
          受保护的委托调用，向下传递所需权限与范围。
          
      en: >
          Guarded delegated call that propagates the required permission and scope.
          
deps:
  - kind: call
    to: pyvdisk.contracts.capability
    from_api: "rpc:pyvdisk.infrastructure.capabilities.CapabilityNamespace#_check"
    to_api: "rpc:pyvdisk.contracts.CapabilityGrant#allows"
    label: {zh: "检查授权", en: "checks grants"}
---
