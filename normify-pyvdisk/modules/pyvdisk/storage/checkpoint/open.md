---
uid: a0000804
id: pyvdisk.storage.checkpoint.open
parent: pyvdisk.storage.checkpoint
name: {zh: "检查点存储", en: "Checkpoint Store"}
description:
  zh: >
      检查点存储的构造与加锁：后端选择、VFS 或宿主背衬，以及独占写周期。
      
  en: >
      Checkpoint store construction and locking: backend selection, VFS or host backing, and the exclusive write cycle.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.308Z"
fingerprint: d96b0e630513ab3bea2172e2d6d091b3f50f62680b86ce05380946d8ce3e3424
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
    to: pyvdisk.storage.vfs.files
    from_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore#from_vfs"
    to_api: "rpc:pyvdisk.vfs.VFS#read_file"
    label: {zh: "经 VFS 读写", en: "reads via VFS"}
---
