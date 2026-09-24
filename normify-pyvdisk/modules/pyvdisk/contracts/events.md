---
uid: a0000110
id: pyvdisk.contracts.events
parent: pyvdisk.contracts
name: {zh: "事件契约", en: "Event Contracts"}
description:
  zh: >
      事件值类型，以及结构化日志使用的追加/读取事件存储协议。
  en: >
      Event value type and the append/read event-store protocol used by the structured log.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 86
    end_line: 96
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.Event"
    description:
      zh: >
          不可变事件：流名、负载、event_id 与时间戳。
      en: >
          Immutable event with stream, payload, event_id and timestamp.
  - protocol: rpc
    path: "pyvdisk.contracts.EventStore"
    description:
      zh: >
          事件流的追加与读取协议。
      en: >
          Append/read event stream protocol.
  - protocol: rpc
    path: "pyvdisk.contracts.EventStore#append"
    description:
      zh: >
          追加一个事件并返回其持久 event id。
      en: >
          Append one event and return its durable event id.
  - protocol: rpc
    path: "pyvdisk.contracts.EventStore#read"
    description:
      zh: >
          从游标之后按可选上限读取某流的事件。
      en: >
          Read events from a stream after a cursor with an optional limit.
---
