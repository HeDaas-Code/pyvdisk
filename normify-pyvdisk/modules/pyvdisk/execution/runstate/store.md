---
uid: a000090b
id: pyvdisk.execution.runstate.store
parent: pyvdisk.execution.runstate
name: {zh: "运行状态存储", en: "Run State Store"}
description:
  zh: >
      运行状态存储：带幂等的创建、受保护状态迁移、列举与过期运行回收。
      
  en: >
      Run state store: create with idempotency, guarded transitions, listing and stale-run recovery.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:22:04.608Z"
fingerprint: 38952ffc815f8771c14753783c0e3da128b6877309ee722d94fe8fb43aa54b97
source:
  - path: "pyvdisk/infrastructure/run_state.py"
    line: 27
    end_line: 87
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore"
    description:
      zh: >
          经检查点存储持久化的带版本运行状态。
          
      en: >
          Versioned run state persisted through a checkpoint store.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore#from_data_disk"
    description:
      zh: >
          从 DataDisk 元数据命名空间构建存储。
          
      en: >
          Build the store from a DataDisk metadata namespace.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore#get"
    description:
      zh: >
          获取单条运行记录。
          
      en: >
          Fetch one run record.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore#list"
    description:
      zh: >
          列出运行记录，可按状态过滤。
          
      en: >
          List run records, optionally filtered by status.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore#create"
    description:
      zh: >
          创建运行记录，并按幂等键去重。
          
      en: >
          Create a run record, deduplicating by idempotency key.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore#transition"
    description:
      zh: >
          执行受版本保护的状态迁移。
          
      en: >
          Apply a version-guarded status transition.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateStore#recover_stale"
    description:
      zh: >
          回收停留在中间状态超过最大时长的运行。
          
      en: >
          Reclaim runs stuck in a transient status beyond a maximum age.
          
deps:
  - kind: call
    to: pyvdisk.storage.checkpoint.open
    from_api: "rpc:pyvdisk.infrastructure.run_state.RunStateStore"
    to_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore"
    label: {zh: "持久化运行", en: "persists runs"}
---
