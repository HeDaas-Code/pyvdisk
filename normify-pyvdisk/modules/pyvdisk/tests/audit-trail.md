---
uid: c92e7198
id: pyvdisk.tests.audit-trail
parent: pyvdisk.tests
tags: [tests, audit]
name: {zh: "审计轨迹用例", en: "Audit Trail Tests"}
description:
  zh: >
      审计轨迹用例：哈希链校验（含在真实日志段内篡改记录）、查询筛选与保留策略。
      
  en: >
      Audit trail tests: hash-chain verification, including a record edited inside a real log segment, query filters and retention.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.211Z"
fingerprint: 90c6498b997b3407cee50ba6ed0b70222f14dcba819b2601da038e021aab0759
source:
  - path: "tests/test_audit_trail.py"
    line: 1
    end_line: 336
apis:
  - protocol: rpc
    path: "tests/test_audit_trail.py"
    description:
      zh: >
          审计写入、哈希链、查询与保留的 29 个用例。
          
      en: >
          29 cases over audit emission, the hash chain, query and retention.
          
deps:
  - kind: call
    to: pyvdisk.vscript.audit.sinks
    from_api: "rpc:tests/test_audit_trail.py"
    to_api: "rpc:pyvdisk.vscript.audit.CheckpointAuditSink#verify"
    label: {zh: "验证审计 Sink", en: "exercises audit sinks"}
---
