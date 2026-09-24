---
uid: a0000e1a
id: pyvdisk.tests.e2e
parent: pyvdisk.tests
name: {zh: "端到端用例", en: "End-to-End Tests"}
description:
  zh: >
      遍历整个基础设施栈的集成用例，含在受限盘上运行脚本。
      
  en: >
      The integration test that walks the whole infrastructure stack, including scripts run against scoped disks.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 84c52b2de4b93cb962695fa0577a6c0ccd31b5d699128631cbf627e7ef60650e
source:
  - path: "tests/test_unified_infrastructure_e2e.py"
apis:
  - protocol: rpc
    path: "tests/test_unified_infrastructure_e2e.py"
    description:
      zh: >
          跨统一栈的端到端基础设施演练。
          
      en: >
          End-to-end infrastructure walkthrough across the unified stack.
          
deps:
  - kind: call
    to: pyvdisk.storage.datadisk.api
    to_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#scoped"
    label: {zh: "驱动 DataDisk", en: "drives DataDisk"}
---
