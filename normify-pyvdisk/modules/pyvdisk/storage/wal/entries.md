---
uid: a0000802
id: pyvdisk.storage.wal.entries
parent: pyvdisk.storage.wal
name: {zh: "WAL 记录", en: "WAL Entries"}
description:
  zh: >
      事务日志动词与崩溃恢复重放。
      
  en: >
      Transaction journal verbs and crash recovery replay.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 43c2df470c8470e355007b640747720bd497fae956929ae151b60094f86c1836
source:
  - path: "pyvdisk/infrastructure/wal.py"
    line: 30
    end_line: 38
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#begin"
    description:
      zh: >
          开启事务并返回其 id。
          
      en: >
          Open a transaction and return its id.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#append"
    description:
      zh: >
          在已开启事务内记录一个操作。
          
      en: >
          Record one operation inside an open transaction.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#prepare"
    description:
      zh: >
          标记事务进入 prepare。
          
      en: >
          Mark a transaction prepared.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#commit"
    description:
      zh: >
          标记事务已提交。
          
      en: >
          Mark a transaction committed.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#abort"
    description:
      zh: >
          标记事务已回滚。
          
      en: >
          Mark a transaction aborted.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#recover"
    description:
      zh: >
          重放日志：对已开启事务调 undo、对已 prepare 未完成事务调 redo。
          
      en: >
          Replay the journal, calling undo for begun and redo for prepared-but-unfinished transactions.
          
---
