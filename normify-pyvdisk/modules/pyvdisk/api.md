---
uid: a0000322
id: pyvdisk.api
parent: pyvdisk
tags: [api]
name: {zh: "公开门面", en: "Public Facade"}
description:
  zh: >
      公开门面：调用方直接从 pyvdisk 包根导入的存储、执行、Agent 与契约名称。
  en: >
      Public facade: the storage, execution, agent and contract names that callers import directly from the pyvdisk package root.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: 829b9ac86974d0b749ac032ca0809ff290509d8be9218da09a8823562bd84a3b
source:
  - path: "pyvdisk/__init__.py"
apis:
  - protocol: rpc
    path: "pyvdisk.VirtualDisk"
    description:
      zh: >
          宿主 .vdisk 文件之上的块设备。
      en: >
          Block device over a host .vdisk file.
  - protocol: rpc
    path: "pyvdisk.VFS"
    description:
      zh: >
          高层路径式虚拟文件系统门面。
      en: >
          High-level path-based virtual filesystem facade.
  - protocol: rpc
    path: "pyvdisk.DataDisk"
    description:
      zh: >
          在包根导出的统一 DataDisk 容器。
      en: >
          Unified DataDisk container exported at the package root.
  - protocol: rpc
    path: "pyvdisk.ExecutionService"
    description:
      zh: >
          在包根导出的执行平面实现。
      en: >
          Execution plane implementation exported at the package root.
  - protocol: rpc
    path: "pyvdisk.DurableQueue"
    description:
      zh: >
          在包根导出的持久任务队列。
      en: >
          Durable task queue exported at the package root.
  - protocol: rpc
    path: "pyvdisk.CheckpointStore"
    description:
      zh: >
          在包根导出的检查点键值存储。
      en: >
          Checkpoint-backed key/value store exported at the package root.
  - protocol: rpc
    path: "pyvdisk.VectorDisk"
    description:
      zh: >
          在包根导出的向量盘。
      en: >
          Vector disk exported at the package root.
  - protocol: rpc
    path: "pyvdisk.RunHandle"
    description:
      zh: >
          执行平面返回的运行句柄。
      en: >
          Run handle returned by the execution plane.
  - protocol: rpc
    path: "pyvdisk.AgentSandbox"
    description:
      zh: >
          Agent 工作区门面：Agent 框架只需要这一个导入。
      en: >
          The agent workspace facade: the one import an agent framework needs.
  - protocol: rpc
    path: "pyvdisk.compat"
    description:
      zh: >
          平台适配层；导出后调用方可以查询当前用的是哪套实现。
      en: >
          The platform layer, exported so callers can ask which implementation is live.
  - protocol: rpc
    path: "pyvdisk.FlatIndex"
    description:
      zh: >
          无外部依赖的精确向量索引。
      en: >
          The dependency-free exact vector index.
deps:
  - kind: reference
    to: pyvdisk.agent.sandbox
    from_api: "rpc:pyvdisk.AgentSandbox"
    label: {zh: "转出沙箱门面", en: "re-exports the sandbox"}
  - kind: reference
    to: pyvdisk.platform
    from_api: "rpc:pyvdisk.compat"
    label: {zh: "转出平台适配层", en: "re-exports the platform layer"}
  - kind: reference
    to: pyvdisk.storage.vector.flat-index
    from_api: "rpc:pyvdisk.FlatIndex"
    label: {zh: "转出扁平索引", en: "re-exports the flat index"}
---
