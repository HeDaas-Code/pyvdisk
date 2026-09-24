---
uid: a000060e
id: pyvdisk.storage.logging.logger
parent: pyvdisk.storage.logging
name: {zh: "统一日志器", en: "Unified Logger"}
description:
  zh: >
      UnifiedLogger：级别门限、上下文与字段合并、标签绑定与异常捕获。
      
  en: >
      UnifiedLogger: level gate, context and field merging, tag binding and exception capture.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: fefd7a882d4b70ff980d0e54e1cafe1b91a0123ff526fca44181377d3f5cdd3f
source:
  - path: "pyvdisk/logging_core.py"
    line: 83
    end_line: 110
apis:
  - protocol: rpc
    path: "pyvdisk.logging_core.UnifiedLogger"
    description:
      zh: >
          把一个事件扇出到多个 sink 的结构化日志器。
          
      en: >
          Structured logger fanning one event out to several sinks.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.UnifiedLogger#bind"
    description:
      zh: >
          返回附带额外绑定字段的日志器。
          
      en: >
          Return a logger with additional bound fields.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.UnifiedLogger#with_tags"
    description:
      zh: >
          返回附带额外字符串标签的日志器。
          
      en: >
          Return a logger with additional string tags.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.UnifiedLogger#log"
    description:
      zh: >
          以显式级别产出一个事件。
          
      en: >
          Emit one event at an explicit level.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.UnifiedLogger#exception"
    description:
      zh: >
          产出携带当前异常信息的 ERROR 事件。
          
      en: >
          Emit an ERROR event carrying the current exception info.
          
deps:
  - kind: event
    to: pyvdisk.storage.logging.sinks
    from_api: "rpc:pyvdisk.logging_core.UnifiedLogger#log"
    to_api: "rpc:pyvdisk.logging_core.LogSink"
    label: {zh: "向 sink 发送", en: "emits to sinks"}
---
