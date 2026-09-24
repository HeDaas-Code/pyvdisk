---
uid: a000030e
id: pyvdisk.storage.wal
parent: pyvdisk.storage
name: {zh: "预写日志", en: "Write-Ahead Log"}
description:
  zh: >
      预写日志：同一套带检查点与截断的分段 WAL，由 DataDisk 事务与 VScript 事务撤销共用，而不是两份并行实现。
      
  en: >
      Write-ahead logging: one segmented WAL implementation with checkpointing and truncation, shared by DataDisk transactions and VScript transaction undo instead of two parallel implementations.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.238Z"
fingerprint: 50ae6934d1990a4ceaed243e96fd51f677869ffe1300820ea255672f1d3868fa
source:
  - path: "pyvdisk/infrastructure/wal.py"
  - path: "pyvdisk/vscript/wal.py"
---
