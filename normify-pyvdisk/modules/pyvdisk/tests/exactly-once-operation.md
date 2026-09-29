---
uid: a0000e0e
id: pyvdisk.tests.exactly-once-operation
parent: pyvdisk.tests
name: {zh: "操作精确一次用例", en: "Exactly-Once Operation Tests"}
description:
  zh: >
      精确一次契约在操作层的半边，经公开执行接口观察。
      
  en: >
      The operation-level half of the exactly-once contract, observed through the public execution surface.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 292b6653c8846015b7c1aacc2741acc8ed7739ebd11f53d15fb182e3d36b3486
source:
  - path: "tests/test_exactly_once_operation.py"
apis:
  - protocol: rpc
    path: "tests/test_exactly_once_operation.py"
    description:
      zh: >
          已提交操作的精确一次语义。
          
      en: >
          Exactly-once semantics for submitted operations.
          
deps:
  - kind: call
    to: pyvdisk.execution.operations.registry
    to_api: "rpc:pyvdisk.infrastructure.operations.OperationRegistry#recover"
    label: {zh: "验证重放", en: "verifies replay"}
---
