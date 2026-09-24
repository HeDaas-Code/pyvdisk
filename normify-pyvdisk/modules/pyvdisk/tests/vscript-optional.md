---
uid: a0000e05
id: pyvdisk.tests.vscript-optional
parent: pyvdisk.tests
name: {zh: "可选链用例", en: "Optional Chain Tests"}
description:
  zh: >
      语言边界用例：可选成员访问如何短路而非报错。
      
  en: >
      Language edge case: how optional member access short-circuits instead of raising.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: e8cb9f8260c13e5b730c465c3939478ae00cb10bc99ba2ded4e2a62fa9b59117
source:
  - path: "tests/test_vscript_optional_chain.py"
apis:
  - protocol: rpc
    path: "tests/test_vscript_optional_chain.py"
    description:
      zh: >
          可选链与空安全成员访问语义。
          
      en: >
          Optional chaining and null-safe member access semantics.
          
deps:
  - kind: call
    to: pyvdisk.vscript.runtime.expressions
    to_api: "rpc:pyvdisk.vscript.runtime.Runtime#eval"
    label: {zh: "验证求值", en: "verifies evaluation"}
---
