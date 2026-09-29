---
uid: a0000e16
id: pyvdisk.tests.queue-backoff
parent: pyvdisk.tests
name: {zh: "退避与锁用例", en: "Backoff and Lock Tests"}
description:
  zh: >
      对指数退避与串行化队列变更的锁的时序敏感用例。
      
  en: >
      Timing-sensitive tests for exponential backoff and the lock that serializes queue mutation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 1a323e73b50428d480ab4d50b6fc70f024fa2199b20d48f34f3593d43c91a527
source:
  - path: "tests/test_queue_backoff_and_lock.py"
apis:
  - protocol: rpc
    path: "tests/test_queue_backoff_and_lock.py"
    description:
      zh: >
          重试退避时序与队列加锁。
          
      en: >
          Retry backoff schedule and queue locking.
          
deps:
  - kind: call
    to: pyvdisk.execution.queue.store
    to_api: "rpc:pyvdisk.infrastructure.queue.DurableQueue#_backoff_seconds"
    label: {zh: "验证退避", en: "verifies backoff"}
---
