---
uid: a0000e19
id: pyvdisk.tests.tx-idempotency
parent: pyvdisk.tests
name: {zh: "事务幂等用例", en: "Transaction Idempotency Tests"}
description:
  zh: >
      小而关键的用例：同一事务提交两次不会产生副作用。
      
  en: >
      Small but critical test that committing the same transaction twice is harmless.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: a6d47e9bf01673f76f415380a7026425bf6c9c2d5406b69189918c4ae324cd7c
source:
  - path: "tests/test_transaction_idempotency.py"
apis:
  - protocol: rpc
    path: "tests/test_transaction_idempotency.py"
    description:
      zh: >
          重复提交下的事务幂等性。
          
      en: >
          Transaction idempotency across repeated commits.
          
deps:
  - kind: call
    to: pyvdisk.storage.datadisk.tx-lifecycle
    to_api: "rpc:pyvdisk.infrastructure.disk.MetadataTransaction#commit"
    label: {zh: "验证幂等", en: "verifies idempotency"}
---
