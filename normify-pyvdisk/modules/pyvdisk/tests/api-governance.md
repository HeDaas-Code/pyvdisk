---
uid: a0000e07
id: pyvdisk.tests.api-governance
parent: pyvdisk.tests
name: {zh: "API 治理用例", en: "API Governance Tests"}
description:
  zh: >
      检查公开能力 API 是否拒绝应当拒绝的调用，而不只验证正常路径。
      
  en: >
      Checks that the public capability API denies what it should, not only that it allows the happy path.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 482a982338fb697d275c3e8f0b731d272c86aec923665e5fb4ab6a0a69aedf30
source:
  - path: "tests/test_api_governance.py"
apis:
  - protocol: rpc
    path: "tests/test_api_governance.py"
    description:
      zh: >
          能力治理接口断言。
          
      en: >
          Capability governance surface assertions.
          
deps:
  - kind: call
    to: pyvdisk.governance.namespace
    to_api: "rpc:pyvdisk.infrastructure.capabilities.CapabilityNamespace#_check"
    label: {zh: "验证范围限定", en: "verifies scoping"}
---
