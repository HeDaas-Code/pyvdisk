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
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T11:41:00.670Z"
fingerprint: 079a5edb2e3962afd8293877a634189cbdef72a96e9d5881983523ef5a531fb1
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
