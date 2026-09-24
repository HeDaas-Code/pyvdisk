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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.236Z"
fingerprint: b09c0a892a4245c749b1b656f75fea42c069ef41438429402f0b180223f5b281
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
