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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: f3bc6b45a520369279ba039c4bf06fb0bfce7e84df609d7d20d81ad24a85dc35
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
