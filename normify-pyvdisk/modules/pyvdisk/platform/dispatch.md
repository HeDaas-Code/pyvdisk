---
uid: a0000330
id: pyvdisk.platform.dispatch
parent: pyvdisk.platform
name: {zh: "实现选择", en: "Implementation Dispatch"}
description:
  zh: >
      决定当前生效的实现并对外描述它。Windows 判定基于 sys.platform；use_implementation() 是测试缝，让模拟分支能在 Linux 上真正被执行；describe() 如实报告当前生效的实现（包括模拟），调用方不会拿到一份"在说另一个平台"的报告。
      
  en: >
      Chooses the implementation in force and describes it. Windows detection is sys.platform based; use_implementation() is the seam that lets the emulated branches be exercised on Linux, and describe() reports what is actually live -- the emulation included -- so a caller never gets a report about a platform that is not the one running.
      
revision: 3cb47877135592bd8565726610c54ebd1ecd9fba
updated_at: "2026-09-24T11:51:39.621Z"
fingerprint: 00f27482df9157d059e546cd531a5773775112816081092a7b689393b4e6197b
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
          当前生效的实现实际会做什么：定位读写、文件锁、目录 fsync、身份与符号链接各由什么原语支撑。描述的是 implementation()，而不是宿主平台。
          
      en: >
          What the implementation in force actually does: which primitive backs positional IO, locking, directory fsync, identity and symlinks. Follows implementation(), not the host platform.
          
---
