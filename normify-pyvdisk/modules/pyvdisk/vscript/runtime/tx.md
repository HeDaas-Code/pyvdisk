---
uid: a0000b01
id: pyvdisk.vscript.runtime.tx
parent: pyvdisk.vscript.runtime
name: {zh: "脚本事务", en: "Script Transaction"}
description:
  zh: >
      脚本事务支持：每个可撤销的 fs 变更在生效前落账，进程内回滚与崩溃恢复走同一个撤销解释器，超过 64 KiB 的快照正文落到事务目录。
      
  en: >
      Script transaction support: every reversible fs change is journalled before it takes effect, in-process rollback and crash recovery run through the same undo interpreter, and snapshot bodies above 64 KiB spill to the transaction area.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.264Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 11
    end_line: 116
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext"
    description:
      zh: >
          收集单次脚本事务的撤销记录与落盘槽位。
          
      en: >
          Collects one script transaction's undo records and its spill slots.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#journal"
    description:
      zh: >
          在效果生效**之前**记入一条可撤销账，大正文落盘而不驻留内存。
          
      en: >
          Journals one reversible effect BEFORE it is applied, spilling large bodies out of memory.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#commit"
    description:
      zh: >
          结算事务并清理其落盘快照。
          
      en: >
          Settles the transaction and drops its spill files.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.TransactionContext#rollback"
    description:
      zh: >
          按逆序通过共享撤销解释器回放账本。
          
      en: >
          Replays the journal in reverse order through the shared undo interpreter.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.recover_wal"
    description:
      zh: >
          崩溃恢复入口：用同一个撤销解释器回放持久化 WAL，并清理遗留快照。
          
      en: >
          Crash-recovery entry point: replays a persisted WAL through the same undo interpreter and drops orphaned spills.
          
deps:
  - kind: call
    to: pyvdisk.vscript.undo
    from_api: "rpc:pyvdisk.vscript.runtime.TransactionContext#rollback"
    label: {zh: "重放撤销记录", en: "replays undo records"}
  - kind: call
    to: pyvdisk.storage.wal.undo
    from_api: "rpc:pyvdisk.vscript.runtime.recover_wal"
    label: {zh: "消费事务 WAL", en: "consumes the tx WAL"}
---
