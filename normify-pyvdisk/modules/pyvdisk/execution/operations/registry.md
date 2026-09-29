---
uid: a0000910
id: pyvdisk.execution.operations.registry
parent: pyvdisk.execution.operations
name: {zh: "操作注册表", en: "Operation Registry"}
description:
  zh: >
      操作注册表门面：存在判定、加载、结果恢复、保存与删除，背衬可为检查点或宿主目录。
      
  en: >
      Operation registry facade: existence, load, result recovery, save and forget, over a checkpoint or host backend.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.308Z"
fingerprint: 6c6d5973baffc84ba17358dc47248de3da2b046dae72d88f9ff96ee9d5fc3bd4
source:
  - path: "pyvdisk/infrastructure/operations.py"
    line: 167
    end_line: 248
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry"
    description:
      zh: >
          存储、加载与重放操作记录的注册表。
          
      en: >
          Registry that stores, loads and replays operation records.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#backend"
    description:
      zh: >
          报告注册表使用的背衬存储。
          
      en: >
          Report which backing store the registry uses.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#has"
    description:
      zh: >
          判断某 operation id 是否已登记。
          
      en: >
          Test whether an operation id is registered.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#load"
    description:
      zh: >
          按 id 加载操作记录。
          
      en: >
          Load an operation record by id.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#recover"
    description:
      zh: >
          返回该操作此前持久化的结果。
          
      en: >
          Return the previously persisted result of an operation.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#save"
    description:
      zh: >
          持久化操作描述并返回其记录。
          
      en: >
          Persist an operation description and return its record.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#forget"
    description:
      zh: >
          删除操作记录。
          
      en: >
          Forget an operation record.
          
deps:
  - kind: call
    to: pyvdisk.storage.checkpoint.open
    from_api: "rpc:pyvdisk.infrastructure.operations.OperationRegistry#save"
    to_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore"
    label: {zh: "经检查点持久化", en: "persists via checkpoint"}
---
