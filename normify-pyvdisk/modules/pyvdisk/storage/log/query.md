---
uid: a0000609
id: pyvdisk.storage.log.query
parent: pyvdisk.storage.log
name: {zh: "日志查询", en: "Log Query"}
description:
  zh: >
      日志盘读取侧：带过滤查询、消费端游标、ack、replay、计数、tail 与实时 follow。
      
  en: >
      Read side of the log disk: filtered queries, consumer cursors, ack, replay, counting, tailing and live follow.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.234Z"
fingerprint: 4b31d03456b1ae4db1ebceef13f447e5093e6459bdea0d2d648139d215bd89a4
source:
  - path: "pyvdisk/log_disk.py"
    line: 149
    end_line: 195
apis:
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#query"
    description:
      zh: >
          按时间窗、级别、logger、tag、属性过滤与上限查询流。
          
      en: >
          Query a stream by time window, level, logger, tag, attribute filter and limit.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#cursor"
    description:
      zh: >
          读取持久化的消费端游标。
          
      en: >
          Read the persisted consumer cursor.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#ack"
    description:
      zh: >
          把消费端游标推进到指定序号。
          
      en: >
          Advance a consumer cursor to a sequence number.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#replay"
    description:
      zh: >
          重放消费端游标之后的全部事件。
          
      en: >
          Re-read everything after the consumer cursor.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#count"
    description:
      zh: >
          统计匹配的事件数。
          
      en: >
          Count matching events.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#tail"
    description:
      zh: >
          按顺序返回最近 n 条匹配事件。
          
      en: >
          Return the last n matching events in order.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#follow"
    description:
      zh: >
          持续产出新追加的事件，直到 stop 事件被设置。
          
      en: >
          Yield new events as they are appended until the stop event is set.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.filter
    from_api: "rpc:pyvdisk.log_disk.LogDisk#query"
    to_api: "rpc:pyvdisk.log_disk._match"
    label: {zh: "应用 where 过滤", en: "applies where-filter"}
---
