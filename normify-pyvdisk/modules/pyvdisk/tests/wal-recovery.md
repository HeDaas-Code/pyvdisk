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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 91f015f9a69c470bcd7c73dd7f5e312415bb1bf2a939050ee144cf3503ae8b06
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
