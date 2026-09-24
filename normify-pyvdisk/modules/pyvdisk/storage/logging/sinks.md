---
uid: a000060d
id: pyvdisk.storage.logging.sinks
parent: pyvdisk.storage.logging
name: {zh: "日志 Sink", en: "Log Sinks"}
description:
  zh: >
      sink 协议及其三种实现：内存、流与日志盘持久化。
      
  en: >
      Sink protocol and its three implementations: memory, stream and log-disk backed persistence.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.237Z"
fingerprint: b09c0a892a4245c749b1b656f75fea42c069ef41438429402f0b180223f5b281
source:
  - path: "pyvdisk/logging_core.py"
    line: 61
    end_line: 81
apis:
  - protocol: rpc
    path: "pyvdisk.logging_core.LogSink"
    description:
      zh: >
          sink 协议：emit、flush 与 close。
          
      en: >
          Sink protocol with emit, flush and close.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.MemorySink"
    description:
      zh: >
          保留最新事件的有界内存 sink。
          
      en: >
          Bounded in-memory sink keeping the newest events.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.StreamSink"
    description:
      zh: >
          向流写入可读行的 sink。
          
      en: >
          Sink writing human-readable lines to a stream.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.LogDiskSink"
    description:
      zh: >
          把事件持久化到日志盘流的 sink。
          
      en: >
          Sink persisting events into a log disk stream.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.append
    from_api: "rpc:pyvdisk.logging_core.LogDiskSink"
    to_api: "rpc:pyvdisk.log_disk.LogDisk#append"
    label: {zh: "追加事件", en: "appends events"}
---
