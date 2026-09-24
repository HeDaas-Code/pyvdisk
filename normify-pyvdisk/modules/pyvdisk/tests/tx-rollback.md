---
uid: a0000e18
id: pyvdisk.tests.tx-rollback
parent: pyvdisk.tests
name: {zh: "事务回滚用例", en: "Transaction Rollback Tests"}
description:
  zh: >
      撤销日志用例：失败事务内的文件系统变更必须被精确还原。
      
  en: >
      The undo-journal test: filesystem mutations inside a failed transaction must be reverted exactly.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 532b14c832235f962c411f2de0ea7f44cf07ba3eeca21d0cd6d7bdef3c729770
source:
  - path: "tests/test_transaction_fs_rollback.py"
apis:
  - protocol: rpc
    path: "tests/test_transaction_fs_rollback.py"
    description:
      zh: >
          经元数据事务的文件系统回滚。
          
      en: >
          Filesystem rollback through the metadata transaction.
          
deps:
  - kind: call
    to: pyvdisk.storage.datadisk.namespace
    to_api: "rpc:pyvdisk.infrastructure.disk.FileNamespace#rmtree"
    label: {zh: "验证回滚", en: "verifies abort"}
---
