---
uid: a0000e0a
id: pyvdisk.tests.contracts
parent: pyvdisk.tests
name: {zh: "契约用例", en: "Contract Tests"}
description:
  zh: >
      保持抽象契约与具体实现一致的合规性用例。
      
  en: >
      Conformance tests that keep the abstract contracts and their concrete implementations aligned.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:22:04.609Z"
fingerprint: 28b37d826e5412d4b3ec6c3bed0679dd1d223682ec4d430269ea1123c1b70b7d
source:
  - path: "tests/test_contracts.py"
apis:
  - protocol: rpc
    path: "tests/test_contracts.py"
    description:
      zh: >
          契约类型的协议一致性断言。
          
      en: >
          Protocol conformance assertions for the contract types.
          
deps:
  - kind: call
    to: pyvdisk.contracts.plane
    to_api: "rpc:pyvdisk.contracts.ExecutionPlane#submit"
    label: {zh: "验证契约", en: "verifies contracts"}
---
