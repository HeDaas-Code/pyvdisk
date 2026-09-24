---
uid: a0000d10
id: pyvdisk.tests.vdisk.locking
parent: pyvdisk.tests.vdisk
name: {zh: "并发用例", en: "Concurrency Tests"}
description:
  zh: >
      并发用例：单独验证锁原语，以及真实并发访问下的 VFS。
  en: >
      Concurrency tests: the locking primitive in isolation and the VFS under real concurrent access.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 1209
    end_line: 1418
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestRWLock"
    description:
      zh: >
          读写锁的获取、升级与超时语义。
      en: >
          Read/write lock acquisition, upgrade and timeout semantics.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestConcurrency"
    description:
      zh: >
          多线程与多进程下的并发 VFS 访问。
      en: >
          Concurrent VFS access under threads and processes.
---
