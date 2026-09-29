---
uid: a000090f
id: pyvdisk.execution.operations.describe
parent: pyvdisk.execution.operations
name: {zh: "操作描述", en: "Operation Description"}
description:
  zh: >
      操作描述：把可调用对象、VScript 源码与裸负载归一为可序列化形态并生成稳定 id。
  en: >
      Operation description: normalizes callables, VScript sources and raw payloads into a serializable shape with a stable id.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 6c6d5973baffc84ba17358dc47248de3da2b046dae72d88f9ff96ee9d5fc3bd4
source:
  - path: "pyvdisk/infrastructure/operations.py"
    line: 127
    end_line: 166
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations._describe_callable"
    description:
      zh: >
          把 Python 可调用对象描述为类型、名称、参数与关键字参数。
      en: >
          Describe a Python callable as kind, name, args and kwargs.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations._describe_vscript"
    description:
      zh: >
          把 VScript 值或源码描述为操作负载。
      en: >
          Describe a VScript value or source as an operation payload.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations._describe_payload"
    description:
      zh: >
          补全操作负载描述的默认值。
      en: >
          Fill in defaults of an operation payload description.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.describe_operation"
    description:
      zh: >
          描述任意受支持操作类型的公开入口。
      en: >
          Public entry point that describes any supported operation kind.
---
