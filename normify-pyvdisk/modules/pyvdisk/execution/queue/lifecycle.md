---
uid: a0000908
id: pyvdisk.execution.queue.lifecycle
parent: pyvdisk.execution.queue
name: {zh: "任务生命周期", en: "Task Lifecycle"}
description:
  zh: >
      任务生命周期：入队、带租约领取、心跳、完成、失败、重试、死信与取消。
  en: >
      Task lifecycle: enqueue, claim with lease, heartbeat, complete, fail, retry, dead-letter and cancel.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1bf87a430e905414842b7c7b482ebffbec2d6d60adc1617411d91f32d3fcd18d
source:
  - path: "pyvdisk/infrastructure/queue.py"
    line: 128
    end_line: 230
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#enqueue"
    description:
      zh: >
          入队负载，并按幂等键去重。
      en: >
          Enqueue a payload, deduplicating by idempotency key.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#claim"
    description:
      zh: >
          领取就绪任务并发放租约。
      en: >
          Claim a ready task and issue a lease.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#heartbeat"
    description:
      zh: >
          延长运行中任务的租约。
      en: >
          Extend the lease of a running task.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#complete"
    description:
      zh: >
          将任务标记为完成，可选带结果。
      en: >
          Mark a task completed with an optional result.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#fail"
    description:
      zh: >
          将任务标记为失败，可选安排重试。
      en: >
          Mark a task failed, optionally scheduling a retry.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#retry"
    description:
      zh: >
          立即重新入队失败或死信任务。
      en: >
          Requeue a failed or dead-lettered task immediately.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#dead_letter"
    description:
      zh: >
          把任务移入死信状态。
      en: >
          Move a task to the dead-letter state.
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#cancel"
    description:
      zh: >
          取消待处理或运行中的任务。
      en: >
          Cancel a pending or running task.
---
