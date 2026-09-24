---
uid: a0000b0f
id: pyvdisk.vscript.audit.sinks
parent: pyvdisk.vscript.audit
name: {zh: "审计 Sink", en: "Audit Sinks"}
description:
  zh: >
      持久审计目的地：检查点存储的有界保留，或日志盘上的只追加审计流。
      
  en: >
      Durable audit destinations: bounded retention in a checkpoint store, or an append-only audit stream on a log disk.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: e6e0c4f6567b6878156a09474961840eaaf3271a6f54be1751ac87c88fbbcebc
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 60
    end_line: 97
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink"
    description:
      zh: >
          把最新记录保存在检查点存储中的审计 sink。
          
      en: >
          Audit sink that keeps the newest records in a checkpoint store.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#emit"
    description:
      zh: >
          持久化一条审计记录。
          
      en: >
          Persist one audit record.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#records"
    description:
      zh: >
          返回保留的审计记录。
          
      en: >
          Return the retained audit records.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink"
    description:
      zh: >
          把记录追加到日志盘流的审计 sink。
          
      en: >
          Audit sink that appends records into a log-disk stream.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink#emit"
    description:
      zh: >
          把一条审计记录追加到 audit 流。
          
      en: >
          Append one audit record to the audit stream.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.append
    from_api: "rpc:pyvdisk.vscript.audit.DataDiskAuditSink#emit"
    to_api: "rpc:pyvdisk.log_disk.LogDisk#append"
    label: {zh: "追加到日志流", en: "appends to log stream"}
  - kind: call
    to: pyvdisk.storage.checkpoint.io
    from_api: "rpc:pyvdisk.vscript.audit.CheckpointAuditSink#emit"
    to_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore#save"
    label: {zh: "经检查点持久化", en: "persists via checkpoint"}
---
