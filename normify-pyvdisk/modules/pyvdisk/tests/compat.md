---
uid: a000033e
id: pyvdisk.tests.compat
parent: pyvdisk.tests
name: {zh: "平台兼容测试", en: "Platform Compat Tests"}
description:
  zh: >
      在 Linux 上执行 Windows 模拟：用 msvcrt 替身加 use_implementation() 让模拟分支在真实文件上运行，覆盖锁竞争与超时分支，并与原生实现逐字节对照一整套操作；同时固定 describe() 描述的是生效实现而不是宿主。替身锁是进程内的，因此无法证明两个进程之间互斥——这仍然需要 Windows runner，文件里写明了这一点。
      
  en: >
      Exercises the Windows emulation from Linux: a stand-in for msvcrt plus use_implementation() runs the emulated branches against real files, including lock contention and the timeout path, and compares a whole workload against the native implementation byte for byte. It also pins describe() to the implementation in force rather than the host. The stand-in's lock is in-process, so it cannot show two processes contending -- that needs a Windows runner, and the file says so.
      
revision: 3cb47877135592bd8565726610c54ebd1ecd9fba
updated_at: "2026-09-24T11:51:39.624Z"
fingerprint: 49ec4bf92e42b64486091b5f313fcab34567167b3fdbe9d85ad538e501c2122d
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
