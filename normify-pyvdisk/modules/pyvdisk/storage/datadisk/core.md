---
uid: a000080c
id: pyvdisk.storage.datadisk.core
parent: pyvdisk.storage.datadisk
name: {zh: "DataDisk 核心", en: "DataDisk Core"}
description:
  zh: >
      DataDisk 构造、元数据原子持久化与挂载时 WAL 恢复。
      
  en: >
      DataDisk construction, atomic metadata persistence and mount-time WAL recovery.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 300
    end_line: 367
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk"
    description:
      zh: >
          把一个 VFS 绑定到文件系统、向量与日志命名空间的统一容器。
          
      en: >
          The unified container binding one VFS to filesystem, vector and log namespaces.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#create"
    description:
      zh: >
          创建并格式化 DataDisk 镜像。
          
      en: >
          Create and format a DataDisk image.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#_atomic_json"
    description:
      zh: >
          经临时文件加 rename 原子写入元数据值。
          
      en: >
          Write a metadata value atomically through a temp file and rename.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#_append_metadata_wal"
    description:
      zh: >
          向元数据 WAL 追加一条记录。
          
      en: >
          Append one record to the metadata WAL.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#_recover_metadata"
    description:
      zh: >
          挂载时重放 WAL，处理未完成事务并清理临时文件。
          
      en: >
          Replay the WAL on mount, resolving unfinished transactions and cleaning temp files.
          
deps:
  - kind: call
    to: pyvdisk.storage.wal.journal
    from_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#_append_metadata_wal"
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog"
    label: {zh: "使用元数据 WAL", en: "uses metadata WAL"}
---
