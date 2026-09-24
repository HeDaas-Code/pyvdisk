---
uid: a0000322
id: pyvdisk.api
parent: pyvdisk
tags: [api]
name: {zh: "公开门面", en: "Public Facade"}
description:
  zh: >
      公开门面：调用方直接从 pyvdisk 包根导入的存储、执行与契约名称。
  en: >
      Public facade: the storage, execution and contract names that callers import directly from the pyvdisk package root.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:14:45.848Z"
fingerprint: 1e6d5c306ceb1123c99b098fd82cda1a805d9c5f23aa12f22d64f3bd129a5da7
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
---
