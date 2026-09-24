---
uid: a000010f
id: pyvdisk.contracts.storage
parent: pyvdisk.contracts
name: {zh: "存储协议", en: "Storage Protocols"}
description:
  zh: >
      结构化存储协议：BlockDevice、NamespaceStore、CollectionStore；既有后端以结构化方式满足它们。
  en: >
      Structural storage protocols: BlockDevice, NamespaceStore and CollectionStore; existing backends satisfy them structurally.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 60
    end_line: 83
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.BlockDevice"
    description:
      zh: >
          面向一层存储后端的定长块 IO 协议。
      en: >
          Fixed-size block IO protocol for layer-1 storage backends.
  - protocol: rpc
    path: "pyvdisk.contracts.NamespaceStore"
    description:
      zh: >
          以路径为键的元数据命名空间协议：get、put、delete、list。
      en: >
          Path-keyed metadata namespace protocol: get, put, delete, list.
  - protocol: rpc
    path: "pyvdisk.contracts.CollectionStore"
    description:
      zh: >
          具名集合协议：create、drop、put、get、scan。
      en: >
          Named collection protocol: create, drop, put, get, scan.
  - protocol: rpc
    path: "pyvdisk.contracts.BlockDevice#read_block"
    description:
      zh: >
          按下标读取一个定长块。
      en: >
          Read one fixed-size block by index.
  - protocol: rpc
    path: "pyvdisk.contracts.BlockDevice#write_block"
    description:
      zh: >
          在指定持久性下写入一个块。
      en: >
          Write one block under a requested durability.
---
