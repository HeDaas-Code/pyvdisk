---
uid: a8e30c5c
id: pyvdisk.tests.wal-checkpoint
parent: pyvdisk.tests
tags: [tests, wal, recovery]
name: {zh: "WAL 检查点用例", en: "WAL Checkpoint Tests"}
description:
  zh: >
      WAL 检查点用例：检查点后的截断、不再全量重放的恢复，以及 DataDisk 与 VScript 共用的同一套实现。
      
  en: >
      WAL checkpoint tests: truncation after a checkpoint, replay without rescanning the full log, and the shared implementation used by both DataDisk and VScript.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.214Z"
fingerprint: 1c79a1bbb852a5a70a892b5919057cfef978163774e48defdcf15c74b4921b8d
source:
  - path: "tests/test_wal_checkpoint_and_recovery.py"
    line: 1
    end_line: 267
apis:
  - protocol: rpc
    path: "tests/test_wal_checkpoint_and_recovery.py"
    description:
      zh: >
          共享 WAL 的检查点、截断与恢复行为。
          
      en: >
          Checkpoint, truncation and recovery behaviour of the shared WAL.
          
deps:
  - kind: call
    to: pyvdisk.storage.wal.entries
    from_api: "rpc:tests/test_wal_checkpoint_and_recovery.py"
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog#recover"
    label: {zh: "验证 WAL 检查点", en: "verifies WAL checkpointing"}
---
