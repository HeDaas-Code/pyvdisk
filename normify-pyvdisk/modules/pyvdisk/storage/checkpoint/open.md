---
uid: a0000804
id: pyvdisk.storage.checkpoint.open
parent: pyvdisk.storage.checkpoint
name: {zh: "检查点存储", en: "Checkpoint Store"}
description:
  zh: >
      检查点存储的构造与加锁：后端选择、VFS 或宿主背衬，以及独占写周期。本模块过去在顶层 import fcntl，导致整个包在 Windows 上无法导入；现在锁来自平台适配层。
      
  en: >
      Checkpoint store construction and locking: backend selection, VFS or host backing, and the exclusive write cycle. This module used to import fcntl at the top level, which made the whole package unimportable on Windows; the lock now comes from the platform layer.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T11:40:40.830Z"
fingerprint: 9ca9673053b671140cc605c35d9a339dee71a77fee8e2598d5b2483bcfd26539
source:
  - path: "pyvdisk/infrastructure/checkpoint.py"
    line: 15
    end_line: 98
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore"
    description:
      zh: >
          带跨进程锁与原子落盘的持久键值存储。
          
      en: >
          Durable key/value store with cross-process locking and atomic saves.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#__init__"
    description:
      zh: >
          基于显式后端或 VFS 路径创建存储。
          
      en: >
          Create a store over an explicit backend or a VFS path.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#from_vfs"
    description:
      zh: >
          构建以已挂载 VFS 为背衬的存储。
          
      en: >
          Build a store backed by a mounted VFS.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#locked"
    description:
      zh: >
          在读-改-写周期内持有跨进程锁的上下文管理器。
          
      en: >
          Context manager holding the cross-process lock for a read-modify-write cycle.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#from_host"
    description:
      zh: >
          构建以宿主目录为背衬的存储。
          
      en: >
          Build a store backed by a host directory.
          
deps:
  - kind: call
    to: pyvdisk.platform.locking
    from_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore#locked"
    label: {zh: "跨进程锁", en: "cross-process lock"}
---
