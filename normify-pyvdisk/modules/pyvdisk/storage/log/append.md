---
uid: a0000608
id: pyvdisk.storage.log.append
parent: pyvdisk.storage.log
name: {zh: "日志追加", en: "Log Append"}
description:
  zh: >
      事件摄入：单条与批量追加，自动分段。
      
  en: >
      Event ingestion: single and batch append with automatic segmentation.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.233Z"
fingerprint: 4b31d03456b1ae4db1ebceef13f447e5093e6459bdea0d2d648139d215bd89a4
source:
  - path: "pyvdisk/log_disk.py"
    line: 104
    end_line: 149
apis:
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#append"
    description:
      zh: >
          追加一个事件，赋予序号、分段与时间戳。
          
      en: >
          Append one event, assigning sequence, segment and timestamp.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#append_many"
    description:
      zh: >
          批量追加事件。
          
      en: >
          Append a batch of events.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.filter
    from_api: "rpc:pyvdisk.log_disk.LogDisk#append"
    to_api: "rpc:pyvdisk.log_disk._json"
    label: {zh: "编码记录", en: "encodes record"}
---
