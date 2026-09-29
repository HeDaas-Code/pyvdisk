---
uid: a0000903
id: pyvdisk.execution.service.queue
parent: pyvdisk.execution.service
name: {zh: "队列驱动执行", en: "Queue-Driven Run"}
description:
  zh: >
      队列驱动的执行：带去重的操作入队，以及带租约处理的领取-运行循环。
      
  en: >
      Queue-driven execution: operation enqueue with dedup, and the claim-and-run loop with lease handling.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.024Z"
fingerprint: 4152ec61e453494829e848f89f2834faa980e43e4bb670d7b0814b68d3187b61
source:
  - path: "pyvdisk/execution.py"
    line: 168
    end_line: 252
apis:
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#enqueue_operation"
    description:
      zh: >
          从提交的操作推导队列状态，并按幂等键去重。
          
      en: >
          Derive queue state from a submitted operation, deduplicating by idempotency key.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#run_next"
    description:
      zh: >
          在租约内领取并运行下一个就绪任务。
          
      en: >
          Claim and run the next ready task within a lease.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#poll_once"
    description:
      zh: >
          未运行 worker 循环时轮询队列一次。
          
      en: >
          Poll the queue once if a worker loop is not running.
          
deps:
  - kind: call
    to: pyvdisk.execution.queue.lifecycle
    from_api: "rpc:pyvdisk.execution.ExecutionService#run_next"
    to_api: "rpc:pyvdisk.infrastructure.queue.DurableQueue#claim"
    label: {zh: "领取任务", en: "claims task"}
---
