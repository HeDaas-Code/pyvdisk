---
uid: a0000335
id: pyvdisk.agent
parent: pyvdisk
name: {zh: "Agent 工作区", en: "Agent Workspace"}
description:
  zh: >
      把 DataDisk 包成可以直接交给 Agent 框架的工作区：工具 schema、调用分发、路径约束与哈希链审计。对接面只有两个调用：tools() 与 dispatch()。
  en: >
      Wraps a DataDisk into a workspace an agent framework can be handed: tool schemas, call dispatch, path confinement and a hash-chained audit trail. The integration surface is two calls, tools() and dispatch().
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 16f85eddeab0b3086fcfd918528a3d307ffcfbfa3cf7f030223ac20f360a198d
source:
  - path: "pyvdisk/sandbox.py"
    line: 198
    end_line: 314
  - path: "pyvdisk/sandbox.py"
    line: 387
    end_line: 474
---
