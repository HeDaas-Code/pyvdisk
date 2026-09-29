---
uid: a0000320
id: pyvdisk.tests
parent: pyvdisk
tags: [tests]
name: {zh: "测试套件", en: "Test Suite"}
description:
  zh: >
      测试套件：447 项可执行校验，覆盖文件系统、卷、身份、锁、队列、事务、VScript、审计轨迹、FUSE 桥、平台适配层、沙箱与打包。缺 hnswlib 时有 4 项对照用例跳过。
      
  en: >
      Test suite: 447 executable checks covering the filesystem, volumes, identity, locking, the queue, transactions, VScript, the audit trail, the FUSE bridge, the platform layer, the sandbox and packaging. Four comparison cases skip when hnswlib is absent.
      
revision: 3cb47877135592bd8565726610c54ebd1ecd9fba
updated_at: "2026-09-24T11:51:39.627Z"
fingerprint: b6440af3d48834c687f05de99c57cf0e3582d53a09d2ffb04b28579e901b64b1
source:
  - path: "tests/conftest.py"
  - path: "tests/test_vdisk.py"
  - path: "tests/test_vscript.py"
---
