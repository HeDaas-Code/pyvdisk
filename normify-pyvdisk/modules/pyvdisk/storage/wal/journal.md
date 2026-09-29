---
uid: a0000801
id: pyvdisk.storage.wal.journal
parent: pyvdisk.storage.wal
name: {zh: "元数据 WAL", en: "Metadata WAL"}
description:
  zh: >
      DataDisk 事务使用的元数据预写日志：存储后端、行编解码，以及分配序号的追加写入。
      
  en: >
      Metadata write-ahead log used by DataDisk transactions: the storage backends, the record codec and the append path that assigns sequence numbers.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.239Z"
fingerprint: 0d8c340fb6943bf9dfde1cc4cb2cb552f203bcc13d2f2ff3586e378c57495e08
source:
  - path: "pyvdisk/infrastructure/wal.py"
    line: 80
    end_line: 106
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog"
    description:
      zh: >
          WAL 本体：存储后端、记录编码与带序号分配的追加。
          
      en: >
          The WAL itself: storage backend, record encoding and append with sequence assignment.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#__init__"
    description:
      zh: >
          把日志绑定到 VFS 路径或宿主文件。
          
      en: >
          Binds the log to a VFS path or a host file.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#append_record"
    description:
      zh: >
          追加一条完整记录，并分配其序号。
          
      en: >
          Appends a fully formed record, allocating its sequence number.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#_append"
    description:
      zh: >
          编码并追加一个 kind/txid 组合。
          
      en: >
          Encodes and appends one kind/txid pair.
          
---
