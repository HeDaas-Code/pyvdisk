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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.246Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
