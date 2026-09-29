---
uid: a0000b0f
id: pyvdisk.vscript.audit.sinks
parent: pyvdisk.vscript.audit
name: {zh: "审计 Sink", en: "Audit Sinks"}
description:
  zh: >
      持久审计目的地：检查点存储里的有界保留，或日志盘上的只追加审计流。两者现在都可读：查询筛选、显式保留、哈希链校验，以及供外部锚定的链头。
      
  en: >
      Durable audit destinations: bounded retention in a checkpoint store, or an append-only audit stream on a log disk. Both are now readable: query filters, explicit retention, hash-chain verification and a head for external anchoring.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.259Z"
fingerprint: e7c398721e85cdb58382b2b377443a1448877191f1be8c698b03443173fc2e4f
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 181
    end_line: 307
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink"
    description:
      zh: >
          把最新记录保存在检查点存储中的审计 Sink。
          
      en: >
          Audit sink that keeps the newest records in a checkpoint store.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#emit"
    description:
      zh: >
          持久化一条审计记录。
          
      en: >
          Persists one audit record.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#records"
    description:
      zh: >
          返回保留的审计记录。
          
      en: >
          Returns the retained audit records.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#query"
    description:
      zh: >
          按运行、任务、状态或时间窗选取记录。
          
      en: >
          Selects records by run, task, status or time window.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#retain"
    description:
      zh: >
          按条数与时间裁剪。
          
      en: >
          Trims by count and age.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#verify"
    description:
      zh: >
          校验哈希链。
          
      en: >
          Verifies the hash chain.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#head"
    description:
      zh: >
          当前链头，供外部锚定。
          
      en: >
          Current chain head, for external anchoring.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.CheckpointAuditSink#adopt"
    description:
      zh: >
          接管一个锚点，使重建的链能与记录值比对。
          
      en: >
          Adopts an anchor so a rebuilt chain can be compared with a recorded one.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink"
    description:
      zh: >
          日志盘上的只追加审计流。
          
      en: >
          Append-only audit stream on a log disk.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink#emit"
    description:
      zh: >
          把一条审计记录追加到 audit 流。
          
      en: >
          Appends one audit record to the audit stream.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink#query"
    description:
      zh: >
          把流读回为记录行。
          
      en: >
          Reads the stream back as rows.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink#retain"
    description:
      zh: >
          保留策略委派给日志盘自身的执行。
          
      en: >
          Delegates retention to the log disk's own enforcement.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.DataDiskAuditSink#verify"
    description:
      zh: >
          在流上校验哈希链。
          
      en: >
          Verifies the chain over the stream.
          
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
