---
uid: a0000803
id: pyvdisk.storage.wal.undo
parent: pyvdisk.storage.wal
name: {zh: "宿主撤销 WAL", en: "Host Undo WAL"}
description:
  zh: >
      VScript 侧的 WAL 入口：独立的宿主路径实现已取消——本模块直接复用同一套 WriteAheadLog，并给出撤销记录使用的 kind 集与编解码。
      
  en: >
      VScript-side WAL entry point: the separate host-path implementation is gone -- this module re-exports the shared WriteAheadLog together with the record kinds and codecs the undo records use.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.239Z"
fingerprint: 52cf7418ca7ca365477273fa2f1cb4ad9c418bddbdc6413489ec12b2689d9015
source:
  - path: "pyvdisk/vscript/wal.py"
    line: 1
    end_line: 11
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.wal.WriteAheadLog"
    description:
      zh: >
          复用同一套 WAL 类，供 VScript 侧使用。
          
      en: >
          The shared WAL class, re-exported for VScript.
          
  - protocol: rpc
    path: "pyvdisk.vscript.wal.RECORD_KINDS"
    description:
      zh: >
          两个平面现在共用的记录种类集合。
          
      en: >
          Record kinds both planes now agree on.
          
  - protocol: rpc
    path: "pyvdisk.vscript.wal.encode_record"
    description:
      zh: >
          与 DataDisk 共用的记录编解码。
          
      en: >
          Record codec shared with DataDisk.
          
  - protocol: rpc
    path: "pyvdisk.vscript.wal.decode_records"
    description:
      zh: >
          与 DataDisk 共用的批量解码。
          
      en: >
          Batch decoder shared with DataDisk.
          
deps:
  - kind: reference
    to: pyvdisk.storage.wal.journal
    from_api: "rpc:pyvdisk.vscript.wal.WriteAheadLog"
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog"
    label: {zh: "复用共享 WAL 实现", en: "reuses the shared WAL"}
---
