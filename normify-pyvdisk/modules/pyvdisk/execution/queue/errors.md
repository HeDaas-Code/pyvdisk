---
uid: a0000905
id: pyvdisk.execution.queue.errors
parent: pyvdisk.execution.queue
name: {zh: "队列错误", en: "Queue Errors"}
description:
  zh: >
      队列错误体系：任务缺失、非法状态迁移与租约丢失。
  en: >
      Queue error taxonomy: missing tasks, invalid transitions and lost leases.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1bf87a430e905414842b7c7b482ebffbec2d6d60adc1617411d91f32d3fcd18d
source:
  - path: "pyvdisk/infrastructure/queue.py"
    line: 19
    end_line: 35
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.QueueError"
    description:
      zh: >
          队列操作的错误基类。
      en: >
          Base error for queue operations.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.TaskNotFound"
    description:
      zh: >
          任务 id 未知时抛出。
      en: >
          Raised when a task id is unknown.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.InvalidTaskState"
    description:
      zh: >
          操作与任务当前状态不符时抛出。
      en: >
          Raised when an operation is invalid for the task's current status.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.LeaseLost"
    description:
      zh: >
          租约过期且任务被回收时抛出。
      en: >
          Raised when a lease expired and the task was reclaimed.
---
