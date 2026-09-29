---
uid: a0000332
id: pyvdisk.platform.locking
parent: pyvdisk.platform
name: {zh: "跨进程文件锁", en: "Cross-Process Locking"}
description:
  zh: >
      跨线程、跨进程的整文件写串行化：POSIX 用 fcntl.flock，Windows 用 msvcrt 字节区间锁。Windows 路径刻意用 LK_NBLCK 轮询：LK_LOCK 约十秒后会报错，而 flock 会一直等下去。
      
  en: >
      Whole-file write serialisation across threads and processes: fcntl.flock on POSIX, an msvcrt byte range on Windows. The Windows path polls with LK_NBLCK on purpose: LK_LOCK errors out after about ten seconds where flock keeps waiting.
      
revision: 3cb47877135592bd8565726610c54ebd1ecd9fba
updated_at: "2026-09-24T14:30:00Z"
fingerprint: 00f27482df9157d059e546cd531a5773775112816081092a7b689393b4e6197b
source:
  - path: "pyvdisk/compat.py"
    line: 128
    end_line: 198
  - path: "pyvdisk/compat.py"
    line: 55
  - path: "pyvdisk/compat.py"
    line: 58
apis:
  - protocol: rpc
    path: "pyvdisk.compat.lock"
    description:
      zh: >
          取得整文件锁。blocking=True 等待，timeout=N 秒后放弃并返回 False，blocking=False 只试一次。返回是否拿到锁。
          
      en: >
          Take the whole-file lock. blocking=True waits, timeout=N seconds gives up and returns False, blocking=False tries once. Returns whether the lock is held.
          
  - protocol: rpc
    path: "pyvdisk.compat.unlock"
    description:
      zh: >
          释放锁。句柄已关闭也能调用，因为卸载路径与出错路径都会走到它。
          
      en: >
          Release the lock. Tolerates an already-closed handle, because unmount and error paths both call it.
          
---
