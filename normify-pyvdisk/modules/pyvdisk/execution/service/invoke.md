---
uid: a0000902
id: pyvdisk.execution.service.invoke
parent: pyvdisk.execution.service
name: {zh: "操作分发", en: "Operation Dispatch"}
description:
  zh: >
      操作分发：受限视图构造与两种执行类型，即 Python 可调用对象与 VScript 源码。
      
  en: >
      Operation dispatch: scoped view construction and the two execution kinds, Python callables and VScript sources.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:22:04.609Z"
fingerprint: 4152ec61e453494829e848f89f2834faa980e43e4bb670d7b0814b68d3187b61
source:
  - path: "pyvdisk/execution.py"
    line: 116
    end_line: 167
apis:
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#_scoped_view"
    description:
      zh: >
          为单次执行上下文构建能力受限的磁盘视图。
          
      en: >
          Build the capability-scoped disk view for one execution context.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#_call"
    description:
      zh: >
          在执行上下文下调用 Python 可调用对象。
          
      en: >
          Invoke a Python callable under an execution context.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#_script"
    description:
      zh: >
          在策略、挂载与审计之下运行 VScript 源码。
          
      en: >
          Run a VScript source under policy, mounts and audit.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#_execute"
    description:
      zh: >
          执行单个操作并把结果记录到句柄上。
          
      en: >
          Execute one operation, recording its outcome on the handle.
          
deps:
  - kind: call
    to: pyvdisk.governance.scoped
    from_api: "rpc:pyvdisk.execution.ExecutionService#_scoped_view"
    to_api: "rpc:pyvdisk.infrastructure.capabilities.scoped"
    label: {zh: "限定能力", en: "scopes capabilities"}
  - kind: call
    to: pyvdisk.vscript.runtime.core
    from_api: "rpc:pyvdisk.execution.ExecutionService#_script"
    to_api: "rpc:pyvdisk.vscript.runtime.Runtime#run"
    label: {zh: "运行 VScript", en: "runs VScript"}
---
