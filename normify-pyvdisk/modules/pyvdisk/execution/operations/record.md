---
uid: a000090d
id: pyvdisk.execution.operations.record
parent: pyvdisk.execution.operations
name: {zh: "操作记录", en: "Operation Record"}
description:
  zh: >
      存储的操作描述及其 JSON 编解码，是稳定 operation id 与幂等性的基础。
  en: >
      The stored operation description and its JSON codec, the basis of stable operation ids and idempotency.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 6c6d5973baffc84ba17358dc47248de3da2b046dae72d88f9ff96ee9d5fc3bd4
source:
  - path: "pyvdisk/infrastructure/operations.py"
    line: 53
    end_line: 73
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRecord"
    description:
      zh: >
          持久化操作记录：id、类型、负载指纹与主体。
      en: >
          Persisted operation record: id, kind, payload fingerprint and body.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRecord#to_json"
    description:
      zh: >
          把记录渲染为可存储形式。
      en: >
          Render the record for storage.
  - protocol: rpc
    path: "pyvdisk.infrastructure.operations.OperationRecord#from_json"
    description:
      zh: >
          从存储重建记录。
      en: >
          Rebuild a record from storage.
---
