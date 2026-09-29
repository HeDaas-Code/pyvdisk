---
uid: a0000e0d
id: pyvdisk.tests.exactly-once-internal
parent: pyvdisk.tests
name: {zh: "内部精确一次用例", en: "Exactly-Once Internal Tests"}
description:
  zh: >
      验证重放操作不会重复生效，即精确一次的核心承诺。
      
  en: >
      Verifies that replaying an operation does not reapply its effect, the core exactly-once promise.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 17d44fe8e8e2577aa76afa13965f5354761454e03ca66fce1a1542115a190b89
source:
  - path: "tests/test_exactly_once_internal.py"
apis:
  - protocol: rpc
    path: "tests/test_exactly_once_internal.py"
    description:
      zh: >
          内部队列操作的精确一次语义。
          
      en: >
          Exactly-once semantics for internal queue operations.
          
deps:
  - kind: call
    to: pyvdisk.execution.operations.registry
    to_api: "rpc:pyvdisk.infrastructure.operations.OperationRegistry#has"
    label: {zh: "验证去重", en: "verifies dedup"}
---
