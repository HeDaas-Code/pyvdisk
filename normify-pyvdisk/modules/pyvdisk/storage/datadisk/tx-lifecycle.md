---
uid: a0000809
id: pyvdisk.storage.datadisk.tx-lifecycle
parent: pyvdisk.storage.datadisk
name: {zh: "事务结局", en: "Transaction Outcome"}
description:
  zh: >
      事务的完整结局：进入、经 WAL 的持久提交、带撤销的回滚，以及异常驱动的自动回滚。
      
  en: >
      End-to-end transaction outcome: entry, durable commit through the WAL, abort with undo, and exception-driven rollback.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 101
    end_line: 158
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
