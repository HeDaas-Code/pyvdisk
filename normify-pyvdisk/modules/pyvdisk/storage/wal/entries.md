---
uid: a0000802
id: pyvdisk.storage.wal.entries
parent: pyvdisk.storage.wal
name: {zh: "WAL 记录", en: "WAL Entries"}
description:
  zh: >
      事务日志动词与崩溃恢复重放：begin/append/prepare/commit/abort，以及重放所依赖的读取入口。
      
  en: >
      Transaction log verbs and crash-recovery replay: begin/append/prepare/commit/abort, plus the readers that replay consumes.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.238Z"
fingerprint: 0d8c340fb6943bf9dfde1cc4cb2cb552f203bcc13d2f2ff3586e378c57495e08
source:
  - path: "pyvdisk/infrastructure/wal.py"
    line: 107
    end_line: 139
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#begin"
    description:
      zh: >
          追加 begin 记录以开启事务。
          
      en: >
          Opens a transaction by appending a begin record.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#append"
    description:
      zh: >
          在已开启的事务中记录一个操作。
          
      en: >
          Records one operation inside an open transaction.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#prepare"
    description:
      zh: >
          标记事务已就绪待提交。
          
      en: >
          Marks the transaction ready to commit.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#commit"
    description:
      zh: >
          标记事务已提交。
          
      en: >
          Marks the transaction committed.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#abort"
    description:
      zh: >
          标记事务已中止。
          
      en: >
          Marks the transaction aborted.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#recover"
    description:
      zh: >
          用传入的 undo/redo 回调重放日志，并报告未能结算的部分。
          
      en: >
          Replays the log through the supplied undo and redo callables, and reports what stayed unresolved.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#_read"
    description:
      zh: >
          解码日志中当前的全部记录。
          
      en: >
          Decodes every record currently in the log.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#_last_sequence"
    description:
      zh: >
          已写入的最大序号。
          
      en: >
          Highest sequence number written so far.
          
---
