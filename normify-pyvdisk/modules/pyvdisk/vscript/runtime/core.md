---
uid: a0000b04
id: pyvdisk.vscript.runtime.core
parent: pyvdisk.vscript.runtime
name: {zh: "解释器核心", en: "Interpreter Core"}
description:
  zh: >
      解释器核心：构造与原生模块安装、带参数的顶层运行，以及撤销与操作登记。
      
  en: >
      Interpreter core: construction and native installation, top-level run with arguments, and undo and operation recording.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.310Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 95
    end_line: 138
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime"
    description:
      zh: >
          树遍历解释器，绑定策略、挂载、标准库、审计与模块根。
          
      en: >
          Tree-walking interpreter binding policy, mounts, stdlib, audit and module roots.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#stringify"
    description:
      zh: >
          把任意脚本值渲染为展示文本。
          
      en: >
          Render any script value as display text.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#run"
    description:
      zh: >
          带参数、绑定与 run id 运行已解析程序。
          
      en: >
          Run a parsed program with arguments, bindings and a run id.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#record_undo"
    description:
      zh: >
          在当前事务中登记撤销回调。
          
      en: >
          Record an undo callback in the active transaction.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#record_operation"
    description:
      zh: >
          登记已执行操作以供审计。
          
      en: >
          Record an executed operation for audit.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#exec_block"
    description:
      zh: >
          在给定作用域内执行一个语句块。
          
      en: >
          Execute a block of statements in a scope.
          
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
