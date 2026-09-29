---
uid: a0000312
id: pyvdisk.execution.queue
parent: pyvdisk.execution
tags: [queue, lease]
name: {zh: "持久任务队列", en: "Durable Queue"}
description:
  zh: >
      DurableQueue：以检查点为背衬的任务队列，支持 claim、lease、心跳、退避重试、死信、取消与过期回收。
  en: >
      DurableQueue: checkpoint-backed task queue with claim, lease, heartbeat, retry with backoff, dead-letter, cancellation and stale-run recovery.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1bf87a430e905414842b7c7b482ebffbec2d6d60adc1617411d91f32d3fcd18d
source:
  - path: "pyvdisk/infrastructure/queue.py"
---
