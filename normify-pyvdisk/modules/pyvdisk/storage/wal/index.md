---
uid: a000030e
id: pyvdisk.storage.wal
parent: pyvdisk.storage
name: {zh: "预写日志", en: "Write-Ahead Log"}
description:
  zh: >
      预写日志：DataDisk 事务用的 VFS 元数据 WAL，以及 VScript 事务撤销用的宿主路径 WAL。
  en: >
      Write-ahead logs: a VFS-backed metadata WAL for DataDisk transactions and a host-path WAL for VScript transaction undo.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: a4a5b3c4756b2611748f7e727407eb351a48ebb75ffcc2d23207d431709d04a2
source:
  - path: "pyvdisk/infrastructure/wal.py"
  - path: "pyvdisk/vscript/wal.py"
---
