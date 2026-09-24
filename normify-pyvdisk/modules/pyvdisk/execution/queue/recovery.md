---
uid: a0000909
id: pyvdisk.execution.queue.recovery
parent: pyvdisk.execution.queue
name: {zh: "队列恢复", en: "Queue Recovery"}
description:
  zh: >
      可观测性与崩溃恢复：过期租约回收，以及任务查询与列举。
  en: >
      Observability and crash recovery: stale-lease reclamation plus task lookup and listing.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1bf87a430e905414842b7c7b482ebffbec2d6d60adc1617411d91f32d3fcd18d
source:
  - path: "pyvdisk/infrastructure/queue.py"
    line: 231
    end_line: 260
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#recover_stale"
    description:
      zh: >
          回收租约过期的任务，重新入队或转死信。
      en: >
          Reclaim tasks whose lease expired and requeue or dead-letter them.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#get"
    description:
      zh: >
          按 id 取单个任务。
      en: >
          Fetch one task by id.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#list"
    description:
      zh: >
          列出任务，可按状态过滤。
      en: >
          List tasks, optionally filtered by status.
---
