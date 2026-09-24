---
uid: a0000906
id: pyvdisk.execution.queue.task
parent: pyvdisk.execution.queue
name: {zh: "队列任务", en: "Queue Task"}
description:
  zh: >
      队列状态中存储的任务值对象，含租约与尝试次数记账。
  en: >
      The task value object stored in the queue state, including lease and attempt bookkeeping.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1bf87a430e905414842b7c7b482ebffbec2d6d60adc1617411d91f32d3fcd18d
source:
  - path: "pyvdisk/infrastructure/queue.py"
    line: 36
    end_line: 57
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.QueueTask"
    description:
      zh: >
          任务记录：id、负载、状态、尝试次数、租约、结果与错误。
      en: >
          Task record: id, payload, status, attempts, lease, result and error.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.QueueTask#from_dict"
    description:
      zh: >
          从持久字典重建任务。
      en: >
          Rebuild a task from its persisted dictionary.
---
