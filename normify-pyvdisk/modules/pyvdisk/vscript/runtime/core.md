---
uid: a0000b04
id: pyvdisk.vscript.runtime.core
parent: pyvdisk.vscript.runtime
name: {zh: "解释器核心", en: "Interpreter Core"}
description:
  zh: >
      解释器核心：构造与原生模块安装、带参数的顶层运行、原生模块调用的记账入口，以及语句块执行。
      
  en: >
      Interpreter core: construction and native-module installation, top-level run with arguments, the journaling entry point native modules call, and statement-block execution.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.262Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 178
    end_line: 223
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime"
    description:
      zh: >
          解释器：策略、挂载、审计 Sink 与事务记账。
          
      en: >
          The interpreter: policy, mounts, audit sink and transaction bookkeeping.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#stringify"
    description:
      zh: >
          按 REPL 的方式渲染一个值。
          
      en: >
          Renders one value the way the REPL prints it.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#run"
    description:
      zh: >
          跑完一个程序并返回结果。
          
      en: >
          Runs a program to completion and returns its result.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#journal"
    description:
      zh: >
          解释器自身的记账入口，供原生模块调用。
          
      en: >
          The interpreter's own journaling entry point, used by native modules.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#transactions_open"
    description:
      zh: >
          当前尚未结算的事务数。
          
      en: >
          How many transactions are still open.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#exec_block"
    description:
      zh: >
          在某个作用域中执行一个语句块。
          
      en: >
          Executes one block of statements in a scope.
          
deps:
  - kind: call
    to: pyvdisk.vscript.policy.budget
    from_api: "rpc:pyvdisk.vscript.runtime.Runtime#run"
    to_api: "rpc:pyvdisk.vscript.policy.Budget#tick"
    label: {zh: "计入预算", en: "charges budget"}
  - kind: event
    to: pyvdisk.vscript.audit.sinks
    from_api: "rpc:pyvdisk.vscript.runtime.Runtime#run"
    to_api: "rpc:pyvdisk.vscript.audit.CheckpointAuditSink#emit"
    label: {zh: "产出审计记录", en: "emits audit records"}
---
