---
uid: a0000e0c
id: pyvdisk.tests.crash-matrix
parent: pyvdisk.tests
name: {zh: "崩溃矩阵用例", en: "Crash Matrix Tests"}
description:
  zh: >
      最强的持久性用例：在每个阶段中断事务并断言恢复后落在合法状态。
      
  en: >
      The strongest durability test: interrupts a transaction at each stage and asserts recovery lands on a legal state.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-24T09:57:44.288Z"
fingerprint: e5dc0b698260945083aefe94df8258b286a859f386a258384ff9e0008f568d27
source:
  - path: "tests/test_datadisk_acid_crash_matrix.py"
apis:
  - protocol: rpc
    path: "tests/test_datadisk_acid_crash_matrix.py"
    description:
      zh: >
          断言 DataDisk 事务 ACID 结果的崩溃点矩阵。
          
      en: >
          Crash-point matrix asserting ACID outcomes for DataDisk transactions.
          
deps:
  - kind: call
    to: pyvdisk.storage.datadisk.core
    from_api: "rpc:tests/test_datadisk_acid_crash_matrix.py"
    to_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#_recover_transactions"
    label: {zh: "验证事务重放", en: "verifies transaction replay"}
---
