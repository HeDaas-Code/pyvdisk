---
uid: a000060a
id: pyvdisk.storage.log.retention
parent: pyvdisk.storage.log
name: {zh: "保留与压缩", en: "Retention and Compaction"}
description:
  zh: >
      日志盘的存储治理：保留策略执行、压缩与统计。
      
  en: >
      Storage hygiene on the log disk: retention enforcement, compaction and statistics.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 11add7318163863decd8c69563dc471bc6d5ad17eb43f77208f2520e3c4397df
source:
  - path: "pyvdisk/log_disk.py"
    line: 196
    end_line: 238
apis:
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#enforce_retention"
    description:
      zh: >
          丢弃超出保留窗口或数量上限的分段与事件。
          
      en: >
          Drop segments and events outside the retention window or count cap.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#compact"
    description:
      zh: >
          通过重写分段压缩流。
          
      en: >
          Compact a stream by rewriting its segments.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#stats"
    description:
      zh: >
          报告每流的分段、事件与字节统计。
          
      en: >
          Report per-stream segment, event and byte statistics.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.streams
    from_api: "rpc:pyvdisk.log_disk.LogDisk#enforce_retention"
    to_api: "rpc:pyvdisk.log_disk.LogDisk#create_stream"
    label: {zh: "读取流配置", en: "reads stream config"}
---
