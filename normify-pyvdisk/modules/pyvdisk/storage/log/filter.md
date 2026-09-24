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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 11add7318163863decd8c69563dc471bc6d5ad17eb43f77208f2520e3c4397df
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
