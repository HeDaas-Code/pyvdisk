---
uid: a000080c
id: pyvdisk.storage.datadisk.core
parent: pyvdisk.storage.datadisk
name: {zh: "DataDisk 核心", en: "DataDisk Core"}
description:
  zh: >
      DataDisk 构造、元数据原子持久化，以及挂载时的 WAL 重放与恢复报告。
      
  en: >
      DataDisk construction, atomic metadata persistence, and the WAL replay performed on mount together with its recovery report.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.226Z"
fingerprint: 9e43dcc0192ae7fcb043dfd6e12b09e42ba36fa2b8b01c445b2e84a45d351d93
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 407
    end_line: 565
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk"
    description:
      zh: >
          磁盘容器本体。
          
      en: >
          The disk container itself.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#create"
    description:
      zh: >
          按容量、块大小与标签创建磁盘镜像。
          
      en: >
          Creates a disk image with a size, block size and label.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#_atomic_json"
    description:
      zh: >
          原子写入 JSON 元数据。
          
      en: >
          Writes JSON metadata atomically.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#_append_metadata_wal"
    description:
      zh: >
          向事务 WAL 追加一条元数据记录。
          
      en: >
          Appends one metadata record to the transaction WAL.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#_recover_transactions"
    description:
      zh: >
          挂载时重放 WAL：已提交事务重做，未提交事务回滚。
          
      en: >
          Replays the WAL on mount: committed transactions redo, uncommitted roll back.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#recovery_report"
    description:
      zh: >
          最近一次恢复对每个事务做了什么。
          
      en: >
          What the last recovery did, per transaction.
          
deps:
  - kind: call
    to: pyvdisk.storage.wal.journal
    from_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#_append_metadata_wal"
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog"
    label: {zh: "使用元数据 WAL", en: "uses metadata WAL"}
---
