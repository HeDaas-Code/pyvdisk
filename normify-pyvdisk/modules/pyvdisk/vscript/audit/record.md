---
uid: a0000b0e
id: pyvdisk.vscript.audit.record
parent: pyvdisk.vscript.audit
name: {zh: "审计记录", en: "Audit Record"}
description:
  zh: >
      解释器、执行服务与 Sink 共用的审计记录形态，含使其可校验（而非仅可追加）的链字段。
      
  en: >
      The audit record shape shared by the interpreter, the execution service and the sinks, including the chain fields that make a trail verifiable rather than merely append-only.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.258Z"
fingerprint: e7c398721e85cdb58382b2b377443a1448877191f1be8c698b03443173fc2e4f
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 160
    end_line: 178
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
