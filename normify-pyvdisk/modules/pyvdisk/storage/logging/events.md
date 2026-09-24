---
uid: a000060b
id: pyvdisk.storage.logging.events
parent: pyvdisk.storage.logging
name: {zh: "日志事件", en: "Log Events"}
description:
  zh: >
      结构化事件值类型及其级别归一与 JSON 转换。
  en: >
      The structured event value type and its level normalization and JSON conversion.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fefd7a882d4b70ff980d0e54e1cafe1b91a0123ff526fca44181377d3f5cdd3f
source:
  - path: "pyvdisk/logging_core.py"
    line: 11
    end_line: 49
apis:
  - protocol: rpc
    path: "pyvdisk.logging_core.normalize_level"
    description:
      zh: >
          把文本或数字级别归一为规范级别名。
      en: >
          Normalize a textual or numeric level into a canonical level name.
  - protocol: rpc
    path: "pyvdisk.logging_core.LogEvent"
    description:
      zh: >
          不可变结构化日志记录：级别、消息、字段、标签、异常与时间戳。
      en: >
          Immutable structured log record with level, message, fields, tags, exception and timestamp.
  - protocol: rpc
    path: "pyvdisk.logging_core.LogEvent#to_dict"
    description:
      zh: >
          把事件转为 JSON 安全的普通字典。
      en: >
          Convert the event into a plain JSON-safe dictionary.
  - protocol: rpc
    path: "pyvdisk.logging_core.LogEvent#from_dict"
    description:
      zh: >
          从字典形式重建事件。
      en: >
          Rebuild an event from its dictionary form.
---
