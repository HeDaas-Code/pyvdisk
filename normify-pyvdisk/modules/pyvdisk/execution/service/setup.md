---
uid: a0000901
id: pyvdisk.execution.service.setup
parent: pyvdisk.execution.service
name: {zh: "服务初始化", en: "Service Setup"}
description:
  zh: >
      ExecutionService 构造与 worker 池控制：同步内联执行与后台处理之间的边界。
      
  en: >
      ExecutionService construction and worker pool control: the boundary between inline execution and background processing.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 4152ec61e453494829e848f89f2834faa980e43e4bb670d7b0814b68d3187b61
source:
  - path: "pyvdisk/execution.py"
    line: 18
    end_line: 115
apis:
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService"
    description:
      zh: >
          同步执行平面，可选后台 worker。
          
      en: >
          Synchronous execution plane, optionally with background workers.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#worker_count"
    description:
      zh: >
          当前运行中的 worker 线程数。
          
      en: >
          Number of worker threads currently running.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#start_workers"
    description:
      zh: >
          启动轮询持久队列的后台 worker 线程。
          
      en: >
          Start background worker threads polling the durable queue.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#stop_workers"
    description:
      zh: >
          停止 worker，可选等待在途任务。
          
      en: >
          Stop workers, optionally waiting for in-flight tasks.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#enqueue_async"
    description:
      zh: >
          把任务加入队列异步执行并返回句柄。
          
      en: >
          Enqueue a task for asynchronous execution and return its handle.
          
deps:
  - kind: call
    to: pyvdisk.execution.queue.store
    from_api: "rpc:pyvdisk.execution.ExecutionService"
    to_api: "rpc:pyvdisk.infrastructure.queue.DurableQueue"
    label: {zh: "持有持久队列", en: "holds durable queue"}
  - kind: call
    to: pyvdisk.storage.datadisk.api
    from_api: "rpc:pyvdisk.execution.ExecutionService"
    to_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#get_metadata"
    label: {zh: "读取元数据", en: "reads metadata"}
---
