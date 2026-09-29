---
uid: a0000e09
id: pyvdisk.tests.checkpoint
parent: pyvdisk.tests
name: {zh: "检查点用例", en: "Checkpoint Tests"}
description:
  zh: >
      为队列、运行、操作与审计提供背衬的持久键值存储的单元用例。
      
  en: >
      Unit tests for the durable key/value store that backs queues, runs, operations and audit.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 58670b8459c125b158d8382488db44266dc27b9f5bec60e375f1c00cd2329fc9
source:
  - path: "tests/test_checkpoint_store.py"
apis:
  - protocol: rpc
    path: "tests/test_checkpoint_store.py"
    description:
      zh: >
          检查点存储的 get、set、save 与加锁。
          
      en: >
          Checkpoint store get, set, save and locking.
          
deps:
  - kind: call
    to: pyvdisk.storage.checkpoint.open
    to_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore"
    label: {zh: "验证存储", en: "verifies store"}
---
