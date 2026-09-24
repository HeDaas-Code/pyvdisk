---
uid: a0000605
id: pyvdisk.storage.log.filter
parent: pyvdisk.storage.log
name: {zh: "日志过滤", en: "Log Filtering"}
description:
  zh: >
      日志记录值过滤与规范 JSON 编码，供追加与查询共用。
      
  en: >
      Log record value filter and canonical JSON encoding shared by append and query.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.234Z"
fingerprint: 4b31d03456b1ae4db1ebceef13f447e5093e6459bdea0d2d648139d215bd89a4
source:
  - path: "pyvdisk/log_disk.py"
    line: 11
    end_line: 37
apis:
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDiskError"
    description:
      zh: >
          日志盘特定失败时抛出。
          
      en: >
          Raised for log-disk specific failures.
          
  - protocol: rpc
    path: "pyvdisk.log_disk._json"
    description:
      zh: >
          每条持久日志记录使用的规范紧凑 JSON 编码。
          
      en: >
          Canonical compact JSON encoding used for every persisted log record.
          
  - protocol: rpc
    path: "pyvdisk.log_disk._match"
    description:
      zh: >
          把记录与嵌套的 where 比较/列表过滤条件匹配。
          
      en: >
          Match a record against a nested where-filter of comparisons and lists.
          
---
