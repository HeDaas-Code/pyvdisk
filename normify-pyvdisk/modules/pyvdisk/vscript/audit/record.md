---
uid: a0000b0e
id: pyvdisk.vscript.audit.record
parent: pyvdisk.vscript.audit
name: {zh: "审计记录", en: "Audit Record"}
description:
  zh: >
      解释器、执行服务与 sink 共用的审计记录形态。
  en: >
      The audit record shape shared by the interpreter, the execution service and the sinks.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: e6e0c4f6567b6878156a09474961840eaaf3271a6f54be1751ac87c88fbbcebc
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 39
    end_line: 58
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.AuditRecord"
    description:
      zh: >
          单条审计记录：run id、脚本与策略哈希、结果、计数与执行平面关联字段。
      en: >
          One audit record: run id, script and policy hashes, outcome, counters and execution-plane correlation.
  - protocol: rpc
    path: "pyvdisk.vscript.audit.AuditRecord#to_dict"
    description:
      zh: >
          把记录渲染为 JSON 安全字典。
      en: >
          Render the record as a JSON-safe dictionary.
---
