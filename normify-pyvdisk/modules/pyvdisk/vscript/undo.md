---
uid: "77079781"
id: pyvdisk.vscript.undo
parent: pyvdisk.vscript
tags: [vscript, transaction, undo, durability]
name: {zh: "事务撤销记账", en: "Transaction Undo Bookkeeping"}
description:
  zh: >
      VScript 事务的撤销记账：每个可撤销的 fs 变更在生效之前就落账，进程内回滚与崩溃恢复共用同一个解释器；超过 64 KiB 的快照正文落到 /.system/tx，不再整份驻留内存。
      
  en: >
      Undo bookkeeping for VScript transactions: every reversible fs change is journalled before it takes effect, the in-process rollback and the crash-recovery pass share one interpreter, and snapshot bodies above 64 KiB spill to /.system/tx instead of staying in memory.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.210Z"
fingerprint: 45715e912e2168183a77a42b313761b2973190999957980141f83dfda88223e2
source:
  - path: "pyvdisk/vscript/undo.py"
    line: 1
    end_line: 210
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.undo.normalize"
    description:
      zh: >
          把一条撤销记录规范化，使进程内回滚与崩溃恢复两个解释器不会漂移。
          
      en: >
          Canonicalises one undo record so the in-process and the crash-recovery interpreters cannot drift apart.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.spill_path"
    description:
      zh: >
          解析存放某个已落盘快照正文的磁盘槽位。
          
      en: >
          Resolves the on-disk slot that holds one spilled snapshot body.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.store_body"
    description:
      zh: >
          保存快照正文，超过阈值时落到事务目录而不是留在内存。
          
      en: >
          Stores a snapshot body, spilling to the transaction area once it exceeds the threshold.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.load_body"
    description:
      zh: >
          读回快照正文，可能来自内存，也可能来自事务目录。
          
      en: >
          Reads back a snapshot body, from memory or from the transaction area.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.snapshot_tree"
    description:
      zh: >
          在递归删除登记逆操作之前，先为整棵子树拍快照。
          
      en: >
          Captures a directory tree before a recursive removal journals reverse operations.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.spill_conflict"
    description:
      zh: >
          当快照位置本身落在待撤销操作的删除范围内时拒绝记账。
          
      en: >
          Refuses a snapshot whose location would itself be removed by the operation it must undo.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.apply_undo"
    description:
      zh: >
          针对某个存储重放一条撤销记录。
          
      en: >
          Replays one undo record against a store.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.discard_spill_area"
    description:
      zh: >
          事务结算后清理遗留的落盘快照文件。
          
      en: >
          Drops orphaned spill files after a transaction settles.
          
  - protocol: rpc
    path: "pyvdisk.vscript.undo.KINDS"
    description:
      zh: >
          撤销解释器认识的全部操作种类。
          
      en: >
          Every operation kind the undo interpreter understands.
          
---
