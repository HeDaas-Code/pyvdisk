---
uid: a0000603
id: pyvdisk.storage.vector.records
parent: pyvdisk.storage.vector
name: {zh: "向量记录", en: "Vector Records"}
description:
  zh: >
      记录 CRUD：维度校验、单条与批量 upsert、获取、删除与计数。
      
  en: >
      Record CRUD: dimension validation, upsert (single and batch), fetch, delete and count.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: ee801e56c4d436543de323aa02bb0c3a4e78339ef28b5c1ec180ad68cee817b0
source:
  - path: "pyvdisk/vector_disk.py"
    line: 165
    end_line: 221
apis:
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#upsert"
    description:
      zh: >
          插入或替换一条带向量与元数据的记录。
          
      en: >
          Insert or replace one record with a vector and metadata.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#upsert_many"
    description:
      zh: >
          单次 flush 内批量 upsert。
          
      en: >
          Batch upsert inside a single flush.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#get"
    description:
      zh: >
          按 id 取一条记录。
          
      en: >
          Fetch one record by id.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#delete"
    description:
      zh: >
          删除一条记录，必要时重建索引。
          
      en: >
          Delete one record, rebuilding the index when needed.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#count"
    description:
      zh: >
          统计集合内记录数。
          
      en: >
          Count the records in a collection.
          
deps:
  - kind: call
    to: pyvdisk.storage.vector.collections
    from_api: "rpc:pyvdisk.vector_disk.VectorDisk#upsert"
    to_api: "rpc:pyvdisk.vector_disk.VectorDisk#create_collection"
    label: {zh: "校验集合", en: "verifies collection"}
---
