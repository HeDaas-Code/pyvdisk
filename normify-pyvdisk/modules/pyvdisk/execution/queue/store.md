---
uid: a0000907
id: pyvdisk.execution.queue.store
parent: pyvdisk.execution.queue
name: {zh: "队列存储", en: "Queue Store"}
description:
  zh: >
      队列存储层：经检查点存储的状态读写，以及重试退避策略。
      
  en: >
      Queue storage layer: state load/save through a checkpoint store and the retry backoff policy.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:22:04.608Z"
fingerprint: 1bf87a430e905414842b7c7b482ebffbec2d6d60adc1617411d91f32d3fcd18d
source:
  - path: "pyvdisk/infrastructure/queue.py"
    line: 58
    end_line: 127
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue"
    description:
      zh: >
          以检查点为背衬的持久任务队列。
          
      en: >
          Checkpoint-backed durable task queue.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#_state"
    description:
      zh: >
          读取整个队列状态。
          
      en: >
          Read the whole queue state.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#_save"
    description:
      zh: >
          持久化整个队列状态。
          
      en: >
          Persist the whole queue state.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#_backoff_seconds"
    description:
      zh: >
          计算某个尝试次数的指数退避延迟。
          
      en: >
          Compute the exponential backoff delay for an attempt number.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#_stamp_next_attempt"
    description:
      zh: >
          设置任务的下次可领取时间。
          
      en: >
          Set the next eligible attempt time on a task.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.queue.DurableQueue#_task"
    description:
      zh: >
          从状态中取单条任务记录。
          
      en: >
          Fetch one task record from the state.
          
deps:
  - kind: call
    to: pyvdisk.storage.checkpoint.io
    from_api: "rpc:pyvdisk.infrastructure.queue.DurableQueue#_save"
    to_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore#save"
    label: {zh: "持久化状态", en: "persists state"}
---
