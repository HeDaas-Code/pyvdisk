---
uid: a0000e10
id: pyvdisk.tests.execution-queue
parent: pyvdisk.tests
name: {zh: "执行队列用例", en: "Execution Queue Tests"}
description:
  zh: >
      把执行服务绑定到持久队列及其租约语义的集成用例。
      
  en: >
      Integration tests binding the execution service to the durable queue and its lease semantics.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: e1d699956e464bd55b5ffba7f477d679d10cb02d3881c076c2a91f7f10db35a9
source:
  - path: "tests/test_execution_queue.py"
apis:
  - protocol: rpc
    path: "tests/test_execution_queue.py"
    description:
      zh: >
          持久队列之上的执行服务。
          
      en: >
          Execution service over the durable queue.
          
deps:
  - kind: call
    to: pyvdisk.execution.service.queue
    to_api: "rpc:pyvdisk.execution.ExecutionService#run_next"
    label: {zh: "验证队列执行", en: "verifies queue run"}
---
