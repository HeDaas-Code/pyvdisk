---
uid: a0000330
id: pyvdisk.platform.dispatch
parent: pyvdisk.platform
name: {zh: "实现选择", en: "Implementation Dispatch"}
description:
  zh: >
      决定当前生效的实现并对外描述它。Windows 判定基于 sys.platform；use_implementation() 是测试缝，让模拟分支能在 Linux 上真正被执行；describe() 如实报告当前实现，调用方不必猜。
      
  en: >
      Chooses the implementation in force and describes it. Windows detection is sys.platform based; use_implementation() is the seam that lets the emulated branches be exercised on Linux, and describe() reports what is actually live so a caller never has to guess.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T11:40:54.220Z"
fingerprint: 079a5edb2e3962afd8293877a634189cbdef72a96e9d5881983523ef5a531fb1
source:
  - path: "pyvdisk/compat.py"
    line: 41
    end_line: 100
apis:
  - protocol: rpc
    path: "pyvdisk.compat.implementation"
    description:
      zh: >
          当前生效的实现：posix 或 windows。
      en: >
          The implementation in force: posix or windows.
  - protocol: rpc
    path: "pyvdisk.compat.use_implementation"
    description:
      zh: >
          临时强制指定实现；上下文管理器，退出时还原，供测试在 Linux 上执行 Windows 分支。
      en: >
          Temporarily force an implementation; a context manager that restores the previous one, used by tests to execute the Windows branches on Linux.
  - protocol: rpc
    path: "pyvdisk.compat.describe"
    description:
      zh: >
          当前实现的可读说明：定位读写、文件锁、目录 fsync、身份与符号链接各由什么原语支撑。
      en: >
          Human-readable description of the live implementation: which primitive backs positional IO, locking, directory fsync, identity and symlinks.
---
