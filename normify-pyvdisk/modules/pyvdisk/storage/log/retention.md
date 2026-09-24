---
uid: a000060a
id: pyvdisk.storage.log.retention
parent: pyvdisk.storage.log
name: {zh: "保留与压缩", en: "Retention and Compaction"}
description:
  zh: >
      日志盘的存储治理：保留策略执行、压缩与统计。保留如今同时清理被删事件的 event_ids 并校验消费者游标，不再留下指向已裁剪位置的游标。
      
  en: >
      Log-disk storage governance: retention enforcement, compaction and statistics. Retention also drops the event ids it removed and re-validates consumer cursors, so it can no longer leave a cursor pointing past the trimmed history.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.235Z"
fingerprint: 4b31d03456b1ae4db1ebceef13f447e5093e6459bdea0d2d648139d215bd89a4
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
