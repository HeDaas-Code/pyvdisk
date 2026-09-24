---
uid: a0000e03
id: pyvdisk.tests.vscript-audit
parent: pyvdisk.tests
name: {zh: "审计用例", en: "Audit Tests"}
description:
  zh: >
      对一次运行后审计记录必须包含的内容，以及两种 sink 均持久化它的断言。
      
  en: >
      Assertions on what an audit record must contain after a run, and that both sinks persist it.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 7441f64b06d467b1fd896ba20567a8b913116ce74d1a39d58d53aecb6975a5fb
source:
  - path: "tests/test_vscript_audit.py"
apis:
  - protocol: rpc
    path: "tests/test_vscript_audit.py"
    description:
      zh: >
          审计记录内容与 sink 行为断言。
          
      en: >
          Audit record content and sink behaviour assertions.
          
deps:
  - kind: call
    to: pyvdisk.vscript.audit.record
    to_api: "rpc:pyvdisk.vscript.audit.AuditRecord"
    label: {zh: "验证审计", en: "verifies audit"}
---
