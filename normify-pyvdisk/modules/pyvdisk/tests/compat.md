---
uid: a000033e
id: pyvdisk.tests.compat
parent: pyvdisk.tests
name: {zh: "平台兼容测试", en: "Platform Compat Tests"}
description:
  zh: >
      在 Linux 上执行 Windows 模拟：用 msvcrt 替身加 use_implementation() 让模拟分支在真实文件上运行，覆盖锁竞争与超时分支，并与原生实现逐字节对照一整套操作。替身锁是进程内的，因此无法证明两个进程之间互斥——这仍然需要 Windows runner，文件里写明了这一点。守卫测试会在 compat.py 之外任何模块直接使用 fcntl、msvcrt、os.pread、os.pwrite 时失败。
  en: >
      Exercises the Windows emulation from Linux: a stand-in for msvcrt plus use_implementation() runs the emulated branches against real files, including lock contention and the timeout path, and compares a whole workload against the native implementation byte for byte. The stand-in's lock is in-process, so it cannot show two processes contending -- that needs a Windows runner, and the file says so. A guard test fails if any module outside compat.py reaches for fcntl, msvcrt, os.pread or os.pwrite.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 27901dc78ca371a0a4fb38f74f89616e6b40b5cf776510c92021ff8155f5970c
source:
  - path: "tests/test_compat.py"
apis:
  - protocol: file
    path: "tests/test_compat.py"
    description:
      zh: >
          把平台切到模拟实现跑整条用例。
      en: >
          Run the whole suite with the platform switched to the emulated implementation.
---
