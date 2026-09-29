---
uid: a0000809
id: pyvdisk.storage.datadisk.tx-lifecycle
parent: pyvdisk.storage.datadisk
name: {zh: "事务结局", en: "Transaction Outcome"}
description:
  zh: >
      事务的完整结局：进入、经 WAL 的持久提交、带撤销的回滚，以及异常驱动的自动回滚。abort 现在先把 intent 落盘，再按逆序在进程内通知每个已登记的 participant，最后才展开文件系统回退。
      
  en: >
      How a transaction ends: enter, durable commit through the WAL, rollback with undo, and exception-driven auto-abort. Abort now persists the intents first and then notifies every enlisted participant in reverse order, in-process, before unwinding the filesystem.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.228Z"
fingerprint: 9e43dcc0192ae7fcb043dfd6e12b09e42ba36fa2b8b01c445b2e84a45d351d93
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 181
    end_line: 244
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#__enter__"
    description:
      zh: >
          以上下文管理器进入事务，冲突时可选重试。
          
      en: >
          Enter the transaction as a context manager, optionally retrying on conflict.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#commit"
    description:
      zh: >
          经 WAL 提交事务，应用元数据与命名空间变更。
          
      en: >
          Commit the transaction through the WAL, applying metadata and namespace changes.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#abort"
    description:
      zh: >
          回滚事务并撤销已记录的文件系统意图。
          
      en: >
          Abort the transaction and unwind recorded filesystem intents.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#__exit__"
    description:
      zh: >
          结束上下文块，成功时提交、异常时回滚。
          
      en: >
          Finish the context block, committing on success and aborting on exception.
          
deps:
  - kind: call
    to: pyvdisk.storage.wal.entries
    from_api: "rpc:pyvdisk.infrastructure.disk.MetadataTransaction#commit"
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog#commit"
    label: {zh: "写入 WAL 记录", en: "writes WAL entries"}
---
