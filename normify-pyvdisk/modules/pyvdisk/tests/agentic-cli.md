---
uid: a0000e06
id: pyvdisk.tests.agentic-cli
parent: pyvdisk.tests
name: {zh: "智能体 CLI 用例", en: "Agentic CLI Tests"}
description:
  zh: >
      面向智能体使用编写的 CLI 用例：可发现的输出与稳定的退出码。
      
  en: >
      CLI tests written for agentic usage: discoverable output and stable exit codes.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: c1ace473de65a09dacb70aacab8d41ae03518f3ec5de3532a95a04a873891510
source:
  - path: "tests/test_agentic_cli.py"
apis:
  - protocol: rpc
    path: "tests/test_agentic_cli.py"
    description:
      zh: >
          智能体驱动的 CLI 工作流用例。
          
      en: >
          Agent-driven CLI workflow tests.
          
deps:
  - kind: call
    to: pyvdisk.cli.main
    to_api: "rpc:pyvdisk.cli.main"
    label: {zh: "驱动入口", en: "drives entry point"}
---
