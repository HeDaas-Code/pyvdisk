---
uid: a0000e0b
id: pyvdisk.tests.queue-crossprocess
parent: pyvdisk.tests
name: {zh: "跨进程队列用例", en: "Cross-Process Queue Tests"}
description:
  zh: >
      证明持久队列的租约与去重保证跨进程边界成立，而非仅限线程。
      
  en: >
      Proves the durable queue's lease and dedup guarantees hold across process boundaries, not only threads.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: c105aaf834a3675ab01196cb358ac332be566ac56d37564606a20b703ba064db
source:
  - path: "tests/test_cross_process_queue.py"
apis:
  - protocol: rpc
    path: "tests/test_cross_process_queue.py"
    description:
      zh: >
          跨独立操作系统进程的队列行为。
          
      en: >
          Queue behaviour across separate OS processes.
          
deps:
  - kind: call
    to: pyvdisk.execution.queue.store
    to_api: "rpc:pyvdisk.infrastructure.queue.DurableQueue"
    label: {zh: "验证跨进程队列", en: "verifies cross-process queue"}
---
