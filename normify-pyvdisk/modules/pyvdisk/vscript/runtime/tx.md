---
uid: a0000b01
id: pyvdisk.vscript.runtime.tx
parent: pyvdisk.vscript.runtime
name: {zh: "脚本事务", en: "Script Transaction"}
description:
  zh: >
      脚本事务支持：撤销与操作记账，以及 transaction 语句使用的提交与回滚。
      
  en: >
      Script transaction support: undo and operation journaling plus commit and rollback used by the transaction statement.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.310Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 9
    end_line: 32
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext"
    description:
      zh: >
          收集单次脚本事务的撤销回调与操作。
          
      en: >
          Collects the undo callbacks and operations of one script transaction.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#add_operation"
    description:
      zh: >
          登记一个操作以供后续重放或审计。
          
      en: >
          Register an operation for later replay or audit.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#add"
    description:
      zh: >
          登记一个撤销回调。
          
      en: >
          Register an undo callback.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#commit"
    description:
      zh: >
          应用全部已记录效果并清空日志。
          
      en: >
          Apply all recorded effects and clear the journal.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#rollback"
    description:
      zh: >
          按逆序撤销已记录效果。
          
      en: >
          Undo recorded effects in reverse order.
          
deps:
  - kind: call
    to: pyvdisk.storage.wal.undo
    from_api: "rpc:pyvdisk.vscript.runtime.TransactionContext#rollback"
    to_api: "rpc:pyvdisk.vscript.wal.WriteAheadLog#recover"
    label: {zh: "撤销宿主写入", en: "undoes host writes"}
---
