---
uid: a0000806
id: pyvdisk.storage.checkpoint.triggers
parent: pyvdisk.storage.checkpoint
name: {zh: "触发器检查点", en: "Trigger Checkpoints"}
description:
  zh: >
      面向触发器的便利层，为调度器提供持久的事件去重保证。
  en: >
      Trigger-facing convenience layer that gives the scheduler durable exactly-once event dedup.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: d96b0e630513ab3bea2172e2d6d091b3f50f62680b86ce05380946d8ce3e3424
source:
  - path: "pyvdisk/infrastructure/checkpoint.py"
    line: 146
    end_line: 152
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#mark_success"
    description:
      zh: >
          记录某触发器已消费某事件 id。
      en: >
          Record that a trigger already consumed an event id.
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#last_event"
    description:
      zh: >
          读取某触发器最近成功处理的事件 id。
      en: >
          Read the last successfully processed event id of a trigger.
deps:
  - kind: reference
    to: pyvdisk.vscript.triggers
    label: {zh: "支撑触发器去重", en: "backs trigger dedup"}
---
