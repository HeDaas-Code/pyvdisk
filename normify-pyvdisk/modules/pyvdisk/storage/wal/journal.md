---
uid: a0000801
id: pyvdisk.storage.wal.journal
parent: pyvdisk.storage.wal
name: {zh: "元数据 WAL", en: "Metadata WAL"}
description:
  zh: >
      DataDisk 事务使用的元数据预写日志：日志存储、行编解码与序号跟踪。
      
  en: >
      Metadata write-ahead log used by DataDisk transactions: journal storage, line codec and sequence tracking.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 43c2df470c8470e355007b640747720bd497fae956929ae151b60094f86c1836
source:
  - path: "pyvdisk/infrastructure/wal.py"
    line: 5
    end_line: 29
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog"
    description:
      zh: >
          VFS JSONL 日志之上的事务事件读写器。
          
      en: >
          Transaction lifecycle event reader/writer over a VFS JSONL journal.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#__init__"
    description:
      zh: >
          把日志绑定到 VFS 与日志路径。
          
      en: >
          Bind the log to a VFS and journal path.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#_read"
    description:
      zh: >
          读取并解析全部日志行。
          
      en: >
          Read and parse every journal line.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#_last_sequence"
    description:
      zh: >
          返回现存的最大序号。
          
      en: >
          Return the highest sequence number present.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.wal.WriteAheadLog#_append"
    description:
      zh: >
          追加一条带类型的日志记录。
          
      en: >
          Append one typed journal record.
          
---
