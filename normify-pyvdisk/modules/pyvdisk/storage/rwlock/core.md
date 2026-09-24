---
uid: a000020c
id: pyvdisk.storage.rwlock.core
parent: pyvdisk.storage.rwlock
name: {zh: "锁核心", en: "Lock Core"}
description:
  zh: >
      锁核心：每线程重入、写者优先，以及仅限唯一读者时的读锁升级。
  en: >
      Lock core: per-thread reentrancy, writer priority and read-to-write upgrade with a single-reader guard.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 102a869f8df4b9493ae35d1e0df2a33e5d36355f636d2e1d0432a50b39a31062
source:
  - path: "pyvdisk/rwlock.py"
    line: 32
    end_line: 122
apis:
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock"
    description:
      zh: >
          可重入、写者优先的读写锁。
      en: >
          Reentrant writer-preferring read-write lock.
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock#acquire_read"
    description:
      zh: >
          获取共享读锁，同线程可重入。
      en: >
          Acquire a shared read lock, reentrant per thread.
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock#release_read"
    description:
      zh: >
          释放当前线程的一层读锁。
      en: >
          Release one level of the current thread read lock.
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock#acquire_write"
    description:
      zh: >
          获取独占写锁，必要时从唯一读者升级。
      en: >
          Acquire the exclusive write lock, upgrading from a sole reader if needed.
  - protocol: rpc
    path: "pyvdisk.rwlock.RWLock#release_write"
    description:
      zh: >
          释放写锁，最外层释放时唤醒所有等待者。
      en: >
          Release the write lock, waking all waiters at the outermost level.
---
