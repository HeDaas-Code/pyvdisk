---
uid: a000060f
id: pyvdisk.storage.logging.bridge
parent: pyvdisk.storage.logging
name: {zh: "日志桥接", en: "Logging Bridge"}
description:
  zh: >
      与标准库 logging 模块的桥接，以及模块级日志器工厂。
      
  en: >
      Bridge to the standard library logging module plus the module-level logger factory.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: fefd7a882d4b70ff980d0e54e1cafe1b91a0123ff526fca44181377d3f5cdd3f
source:
  - path: "pyvdisk/logging_core.py"
    line: 112
    end_line: 125
apis:
  - protocol: rpc
    path: "pyvdisk.logging_core.StandardLoggingHandler"
    description:
      zh: >
          把标准库日志记录转发到 sink 的 handler。
          
      en: >
          stdlib logging handler that forwards records into a sink.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.get_logger"
    description:
      zh: >
          按名称、sink 与级别创建 UnifiedLogger 的工厂。
          
      en: >
          Factory building a UnifiedLogger with the given name, sinks and level.
          
deps:
  - kind: call
    to: pyvdisk.storage.logging.sinks
    from_api: "rpc:pyvdisk.logging_core.StandardLoggingHandler"
    to_api: "rpc:pyvdisk.logging_core.LogSink"
    label: {zh: "转发到 sink", en: "forwards to sinks"}
---
