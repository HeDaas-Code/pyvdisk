---
uid: a000033c
id: pyvdisk.examples.quickstart
parent: pyvdisk.examples
name: {zh: "快速上手", en: "Quickstart Tour"}
description:
  zh: >
      单文件、仅标准库、Windows 与 Linux 通用。从裸块设备一路走到 AgentSandbox，跑一遍就能看清分层，并如实报告用的是哪个索引后端。测试在屏蔽 hnswlib 的子进程里跑它，这正是它能当好"最初五分钟"的原因。
  en: >
      One file, standard library only, Windows and Linux. It walks from a raw block device up to AgentSandbox so the layering is visible in one run, and reports which index backend it got. Tests run it in a subprocess with hnswlib blocked, which is what keeps this usable as a first five minutes.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 366abf85eb8b872da8170a251e0d9afc62647e6ff779753eeac8db7c8900e224
source:
  - path: "examples/quickstart.py"
apis:
  - protocol: file
    path: "examples/quickstart.py"
    description:
      zh: >
          在一个进程里自底向上跑通整条栈：块设备、事务、向量检索、日志、VScript，最后是沙箱。
      en: >
          Run the whole stack bottom-up in one process: block device, transactions, vector search, logs, VScript, then the sandbox.
---
