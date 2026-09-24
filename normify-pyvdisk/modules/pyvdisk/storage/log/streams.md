---
uid: a0000607
id: pyvdisk.storage.log.streams
parent: pyvdisk.storage.log
name: {zh: "日志流", en: "Log Streams"}
description:
  zh: >
      流目录：带保留策略的创建、列举与删除。
      
  en: >
      Stream catalogue: creation with retention policy, listing and removal.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.235Z"
fingerprint: 4b31d03456b1ae4db1ebceef13f447e5093e6459bdea0d2d648139d215bd89a4
source:
  - path: "pyvdisk/log_disk.py"
    line: 81
    end_line: 103
apis:
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#create_stream"
    description:
      zh: >
          创建流：段大小、保留窗口与最大事件数。
          
      en: >
          Create a stream with segment size, retention window and max event count.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#list_streams"
    description:
      zh: >
          列出流名称及其配置与计数。
          
      en: >
          List stream names with their configuration and counters.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#drop_stream"
    description:
      zh: >
          删除流及其分段。
          
      en: >
          Drop a stream and its segments.
          
---
