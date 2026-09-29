---
uid: a0000331
id: pyvdisk.platform.positional
parent: pyvdisk.platform
name: {zh: "定位读写", en: "Positioned IO"}
description:
  zh: >
      不依赖也不改动文件游标的原子定位读写。模拟实现不只是方便：没有那把锁，两个线程共用一个句柄时会互相越位 seek，直接写坏数据块。
      
  en: >
      Atomic positioned reads and writes that neither depend on nor disturb the file cursor. The emulation is not merely a convenience: without the lock, two threads sharing a handle would seek past each other and corrupt blocks.
      
revision: 3cb47877135592bd8565726610c54ebd1ecd9fba
updated_at: "2026-09-24T14:30:00Z"
fingerprint: 00f27482df9157d059e546cd531a5773775112816081092a7b689393b4e6197b
source:
  - path: "pyvdisk/compat.py"
    line: 102
    end_line: 127
apis:
  - protocol: rpc
    path: "pyvdisk.compat.pread"
    description:
      zh: >
          从 offset 处读取至多 length 字节。POSIX 用 os.pread；模拟实现用进程级互斥锁包住 lseek+read，避免与其它线程的 seek 交错。
          
      en: >
          Positioned read of up to length bytes. POSIX uses os.pread; the emulation holds a process-wide lock across lseek+read so the pair is not interleaved with another thread's seek.
          
  - protocol: rpc
    path: "pyvdisk.compat.pwrite"
    description:
      zh: >
          向 offset 处写入。POSIX 用 os.pwrite；模拟实现用同一把锁串行化 seek+write。
          
      en: >
          Positioned write. POSIX uses os.pwrite; the emulation serialises seek+write under the same lock.
          
---
