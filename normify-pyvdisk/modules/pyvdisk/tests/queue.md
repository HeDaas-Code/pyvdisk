---
uid: a0000e15
id: pyvdisk.tests.queue
parent: pyvdisk.tests
name: {zh: "队列用例", en: "Queue Tests"}
description:
  zh: >
      单进程内持久队列的状态迁移用例。
      
  en: >
      State-transition tests for the durable queue in a single process.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: d4b22a397ef34fa02381b197ff3d1de54be30621cf995082984de8aff1ac5bb8
source:
  - path: "tests/test_queue.py"
apis:
  - protocol: rpc
    path: "tests/test_queue.py"
    description:
      zh: >
          持久队列单元用例。
          
      en: >
          Durable queue unit tests.
          
deps:
  - kind: call
    to: pyvdisk.execution.queue.lifecycle
    to_api: "rpc:pyvdisk.infrastructure.queue.DurableQueue#claim"
    label: {zh: "验证队列", en: "verifies queue"}
---
