---
uid: a000090c
id: pyvdisk.execution.operations.errors
parent: pyvdisk.execution.operations
name: {zh: "操作错误", en: "Operation Errors"}
description:
  zh: >
      操作注册表错误体系：未知操作与不可序列化操作。
  en: >
      Operation registry error taxonomy covering unknown and unserializable operations.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 6c6d5973baffc84ba17358dc47248de3da2b046dae72d88f9ff96ee9d5fc3bd4
source:
  - path: "pyvdisk/infrastructure/operations.py"
    line: 40
    end_line: 52
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationError"
    description:
      zh: >
          操作注册表的错误基类。
      en: >
          Base error for the operation registry.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationNotFound"
    description:
      zh: >
          operation id 未知时抛出。
      en: >
          Raised when an operation id is unknown.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.UnserializableOperation"
    description:
      zh: >
          操作负载无法序列化时抛出。
      en: >
          Raised when an operation payload cannot be serialized.
---
