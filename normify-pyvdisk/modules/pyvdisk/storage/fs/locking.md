---
uid: a0000401
id: pyvdisk.storage.fs.locking
parent: pyvdisk.storage.fs
name: {zh: "FS 加锁", en: "FS Locking"}
description:
  zh: >
      逐方法读写加锁，以及让同一镜像上的多个 FS 实例互斥的跨实例锁注册表。
      
  en: >
      Per-method read/write locking plus the cross-instance lock registry that makes concurrent FS instances over one image mutually exclusive.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 32
    end_line: 79
apis:
  - protocol: rpc
    path: "pyvdisk.fs._read_locked"
    description:
      zh: >
          用共享读锁包裹方法。
          
      en: >
          Wrap a method with the shared read lock.
          
  - protocol: rpc
    path: "pyvdisk.fs._write_locked"
    description:
      zh: >
          用独占写锁包裹方法。
          
      en: >
          Wrap a method with the exclusive write lock.
          
  - protocol: rpc
    path: "pyvdisk.fs._disk_lock_key"
    description:
      zh: >
          根据盘/卷背后的真实路径推导稳定锁键。
          
      en: >
          Derive a stable lock key from the real paths behind a disk or volume.
          
  - protocol: rpc
    path: "pyvdisk.fs._shared_lock_for"
    description:
      zh: >
          返回同一镜像上所有实例共享的进程级 RWLock。
          
      en: >
          Return the process-wide RWLock shared by all instances over the same image.
          
deps:
  - kind: call
    to: pyvdisk.storage.rwlock.core
    from_api: "rpc:pyvdisk.fs._shared_lock_for"
    to_api: "rpc:pyvdisk.rwlock.RWLock"
    label: {zh: "创建读写锁", en: "creates RWLock"}
---
