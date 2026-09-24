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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 11add7318163863decd8c69563dc471bc6d5ad17eb43f77208f2520e3c4397df
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
