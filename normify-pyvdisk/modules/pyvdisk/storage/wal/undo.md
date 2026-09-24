---
uid: a0000803
id: pyvdisk.storage.wal.undo
parent: pyvdisk.storage.wal
name: {zh: "宿主撤销 WAL", en: "Host Undo WAL"}
description:
  zh: >
      预写日志的宿主文件系统变体：生命周期动词一致，但记录旧文件内容以便事务失败时撤销。
      
  en: >
      Host-filesystem variant of the write-ahead log: same lifetime verbs but records the previous file body so a failed transaction can be undone.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:22:04.609Z"
fingerprint: db40c61d0287aa74638316dbb877367db4fda76f270bdefb13e13f200b0a991c
source:
  - path: "pyvdisk/vscript/wal.py"
    line: 1
    end_line: 61
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.wal.WriteAheadLog"
    description:
      zh: >
          用于 VScript 事务撤销的宿主路径预写日志。
          
      en: >
          Host-path write-ahead log used for VScript transaction undo.
          
  - protocol: rpc
    path: "pyvdisk.vscript.wal.WriteAheadLog#_append"
    description:
      zh: >
          追加一条携带旧文件内容的二进制帧记录。
          
      en: >
          Append one binary-framed record carrying the previous file body.
          
  - protocol: rpc
    path: "pyvdisk.vscript.wal.WriteAheadLog#recover"
    description:
      zh: >
          重放日志，通过 undo 回调恢复旧内容。
          
      en: >
          Replay the log, restoring previous bodies through the undo callback.
          
deps:
  - kind: reference
    to: pyvdisk.storage.wal.journal
    from_api: "rpc:pyvdisk.vscript.wal.WriteAheadLog"
    to_api: "rpc:pyvdisk.infrastructure.wal.WriteAheadLog"
    label: {zh: "沿用 VFS WAL 的设计", en: "mirrors the VFS WAL design"}
---
