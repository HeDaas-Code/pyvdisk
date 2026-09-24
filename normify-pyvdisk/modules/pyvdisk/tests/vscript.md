---
uid: a0000e02
id: pyvdisk.tests.vscript
parent: pyvdisk.tests
name: {zh: "VScript 用例", en: "VScript Tests"}
description:
  zh: >
      VScript 语言用例加上针对真实盘的端到端运行，是全套件中最广的单个测试模块。
      
  en: >
      VScript language tests plus the end-to-end run against real disks, the broadest single test module of the suite.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: b5eb8d42d0e0d9313171bb65d64aa35be955e1cd5f91c4146acafb1bd2feb6f7
source:
  - path: "tests/test_vscript.py"
apis:
  - protocol: rpc
    path: "tests/test_vscript.py::FakeFS"
    description:
      zh: >
          驱动原生 fs 接口的内存 VFS 替身。
          
      en: >
          In-memory VFS double exercising the native fs surface.
          
  - protocol: rpc
    path: "tests/test_vscript.py::VScriptTests"
    description:
      zh: >
          语言与原生模块单元用例：词法、事务、任务、能力与资源限额。
          
      en: >
          Language and native-module unit tests: lexing, transactions, tasks, capabilities and resource limits.
          
  - protocol: rpc
    path: "tests/test_vscript.py::VScriptEndToEndTests"
    description:
      zh: >
          针对真实文件系统、向量与日志盘的端到端脚本执行。
          
      en: >
          End-to-end script execution against real filesystem, vector and log disks.
          
deps:
  - kind: call
    to: pyvdisk.vscript.runtime.core
    to_api: "rpc:pyvdisk.vscript.runtime.Runtime#run"
    label: {zh: "验证解释器", en: "exercises interpreter"}
---
