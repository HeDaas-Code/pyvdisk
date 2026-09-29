---
uid: a0000e1b
id: pyvdisk.tests.wal-recovery
parent: pyvdisk.tests
name: {zh: "WAL 恢复用例", en: "WAL Recovery Tests"}
description:
  zh: >
      日志重放的专项用例：已回滚事务在恢复后必须不可见。
      
  en: >
      Focused test of journal replay: an aborted transaction must be invisible after recovery.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.253Z"
fingerprint: 460baab1c07bd01c140b0540d8220942e6c883f3296de958426ed0a0d999e514
source:
  - path: "tests/test_wal_abort_recovery.py"
apis:
  - protocol: rpc
    path: "tests/test_wal_abort_recovery.py"
    description:
      zh: >
          回滚与崩溃后的 WAL 重放。
          
      en: >
          WAL replay after abort and crash.
          
deps:
  - kind: call
    to: pyvdisk.storage.wal.entries
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog#recover"
    label: {zh: "验证 WAL 恢复", en: "verifies WAL recovery"}
---
