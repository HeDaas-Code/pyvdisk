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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 11add7318163863decd8c69563dc471bc6d5ad17eb43f77208f2520e3c4397df
source:
  - path: "pyvdisk/log_disk.py"
    line: 104
    end_line: 148
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
