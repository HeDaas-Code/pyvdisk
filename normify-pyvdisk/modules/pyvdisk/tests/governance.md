---
uid: a0000e11
id: pyvdisk.tests.governance
parent: pyvdisk.tests
name: {zh: "治理回归用例", en: "Governance Regression Tests"}
description:
  zh: >
      最大的治理测试模块：治理工作新增的受限命名空间的回归覆盖。
      
  en: >
      The largest governance test module: regression coverage for the scoped namespaces added by the governance work.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 7be89d6d2739119b30c106932c8b649e55b6d6eff296a9a6596df647a362eb7f
source:
  - path: "tests/test_governance_regression.py"
apis:
  - protocol: rpc
    path: "tests/test_governance_regression.py"
    description:
      zh: >
          能力治理层的回归用例集。
          
      en: >
          Regression suite for the capability governance layer.
          
deps:
  - kind: call
    to: pyvdisk.governance.files
    to_api: "rpc:pyvdisk.infrastructure.capabilities.ScopedFileNamespace#_check_file"
    label: {zh: "验证受限文件系统", en: "verifies scoped fs"}
---
