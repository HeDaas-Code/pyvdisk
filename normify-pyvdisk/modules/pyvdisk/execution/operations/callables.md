---
uid: a000090e
id: pyvdisk.execution.operations.callables
parent: pyvdisk.execution.operations
name: {zh: "可调用对象注册表", en: "Callable Registry"}
description:
  zh: >
      可调用对象注册表，以及把 Python 函数变为可持久重放操作的 RegisteredCallable 包装。
  en: >
      Callable registry and the RegisteredCallable wrapper that makes a Python function a durable, replayable operation.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 6c6d5973baffc84ba17358dc47248de3da2b046dae72d88f9ff96ee9d5fc3bd4
source:
  - path: "pyvdisk/infrastructure/operations.py"
    line: 74
    end_line: 126
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.register_callable"
    description:
      zh: >
          以稳定名称注册可调用对象以便后续解析。
      en: >
          Register a callable under a stable name for later resolution.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.registered_callables"
    description:
      zh: >
          返回名称到可调用对象的注册表快照。
      en: >
          Return the registry snapshot of name to callable.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations._clear_callables"
    description:
      zh: >
          清空进程级可调用对象注册表。
      en: >
          Clear the process-wide callable registry.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.RegisteredCallable"
    description:
      zh: >
          可调用对象及预绑定参数，可按名解析并可重放。
      en: >
          A callable plus pre-bound arguments, resolvable by name and replayable.
---
