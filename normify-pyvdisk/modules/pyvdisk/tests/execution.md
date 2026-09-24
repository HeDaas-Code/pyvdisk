---
uid: a0000e0f
id: pyvdisk.tests.execution
parent: pyvdisk.tests
name: {zh: "执行用例", en: "Execution Tests"}
description:
  zh: >
      执行平面用例：分发、受限视图与结果传递。
      
  en: >
      Execution plane tests: dispatch, scoped views and result propagation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: ae3435ad777cc2c8e8187f3907169284a12cad7c2f5d3ba172a6d87599f9ae7b
source:
  - path: "tests/test_execution.py"
apis:
  - protocol: rpc
    path: "tests/test_execution.py"
    description:
      zh: >
          执行服务的 submit、run 与策略行为。
          
      en: >
          Execution service submit, run and policy behaviour.
          
deps:
  - kind: call
    to: pyvdisk.execution.service.submit
    to_api: "rpc:pyvdisk.execution.ExecutionService#run"
    label: {zh: "验证服务", en: "verifies service"}
---
