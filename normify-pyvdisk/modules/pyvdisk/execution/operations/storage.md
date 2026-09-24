---
uid: a0000911
id: pyvdisk.execution.operations.storage
parent: pyvdisk.execution.operations
name: {zh: "注册表存储", en: "Registry Storage"}
description:
  zh: >
      背衬访问与可调用对象解析，注册表的最底层。
  en: >
      Backend access and callable resolution, the lowest layer of the registry.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 6c6d5973baffc84ba17358dc47248de3da2b046dae72d88f9ff96ee9d5fc3bd4
source:
  - path: "pyvdisk/infrastructure/operations.py"
    line: 249
    end_line: 324
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#_raw_get"
    description:
      zh: >
          从背衬读取裸操作值。
      en: >
          Read a raw operation value from the backend.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#_raw_put"
    description:
      zh: >
          向背衬写入裸操作值。
      en: >
          Write a raw operation value to the backend.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRegistry#_resolve_callable"
    description:
      zh: >
          把已注册的可调用对象名解析回 Python 可调用对象。
      en: >
          Resolve a registered callable name back to a Python callable.
---
