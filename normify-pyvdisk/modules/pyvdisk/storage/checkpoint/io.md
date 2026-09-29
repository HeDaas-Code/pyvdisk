---
uid: a0000805
id: pyvdisk.storage.checkpoint.io
parent: pyvdisk.storage.checkpoint
name: {zh: "检查点 IO", en: "Checkpoint IO"}
description:
  zh: >
      检查点 IO：键值记录映射的加载、读取、暂存与原子保存。
      
  en: >
      Checkpoint IO: load, read, stage and atomically save the key/value record map.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: 9ca9673053b671140cc605c35d9a339dee71a77fee8e2598d5b2483bcfd26539
source:
  - path: "pyvdisk/infrastructure/checkpoint.py"
    line: 99
    end_line: 145
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#_load"
    description:
      zh: >
          从背衬存储加载记录映射。
          
      en: >
          Load the record map from the backing store.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#get"
    description:
      zh: >
          读取单个检查点值。
          
      en: >
          Read one checkpoint value.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#set"
    description:
      zh: >
          把单个检查点值写入内存映射。
          
      en: >
          Write one checkpoint value into the in-memory map.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.checkpoint.CheckpointStore#save"
    description:
      zh: >
          原子地持久化整个记录映射。
          
      en: >
          Atomically persist the whole record map.
          
---
