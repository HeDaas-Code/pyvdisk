---
uid: a000020d
id: pyvdisk.storage.rwlock.ctx
parent: pyvdisk.storage.rwlock
name: {zh: "锁上下文", en: "Lock Contexts"}
description:
  zh: >
      供 FS 锁装饰器与 VFS/FS 公开接口使用的 with 语句辅助类型。
      
  en: >
      with-statement helpers used by the FS lock decorators and the VFS/FS public surface.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 102a869f8df4b9493ae35d1e0df2a33e5d36355f636d2e1d0432a50b39a31062
source:
  - path: "pyvdisk/rwlock.py"
    line: 124
    end_line: 145
apis:
  - protocol: rpc
    path: "pyvdisk.rwlock.ReadCtx"
    description:
      zh: >
          获取共享读锁的上下文管理器。
          
      en: >
          Context manager acquiring the shared read lock.
          
  - protocol: rpc
    path: "pyvdisk.rwlock.WriteCtx"
    description:
      zh: >
          获取独占写锁的上下文管理器。
          
      en: >
          Context manager acquiring the exclusive write lock.
          
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock#read"
    description:
      zh: >
          构造读锁上下文管理器。
          
      en: >
          Build a read-lock context manager.
          
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock#write"
    description:
      zh: >
          构造写锁上下文管理器。
          
      en: >
          Build a write-lock context manager.
          
deps:
  - kind: call
    to: pyvdisk.storage.rwlock.core
    from_api: "rpc:pyvdisk.rwlock.ReadCtx"
    to_api: "rpc:pyvdisk.rwlock.RWLock#acquire_read"
    label: {zh: "获取读锁", en: "acquires read lock"}
---
