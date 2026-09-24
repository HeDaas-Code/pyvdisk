---
uid: a0000604
id: pyvdisk.storage.vector.search
parent: pyvdisk.storage.vector
name: {zh: "向量检索", en: "Vector Search"}
description:
  zh: >
      HNSW 图上的索引管理与相似度检索，支持元数据过滤。
      
  en: >
      Index management and similarity search over the HNSW graph with metadata filtering.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: f3bc6b45a520369279ba039c4bf06fb0bfce7e84df609d7d20d81ad24a85dc35
source:
  - path: "pyvdisk/vector_disk.py"
    line: 223
    end_line: 267
apis:
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#_rebuild_index"
    description:
      zh: >
          从持久记录重建 HNSW 索引。
          
      en: >
          Rebuild the HNSW index from the persisted records.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#_load_index"
    description:
      zh: >
          加载盘上索引，缺失时重建。
          
      en: >
          Load the on-disk index or rebuild it when absent.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#search"
    description:
      zh: >
          相似度检索：k 结果、可选元数据过滤，以及是否返回向量。
          
      en: >
          Similarity search with k results, an optional metadata filter and include/exclude of vectors.
          
deps:
  - kind: dataflow
    to: pyvdisk.storage.vector.records
    from_api: "rpc:pyvdisk.vector_disk.VectorDisk#_rebuild_index"
    to_api: "rpc:pyvdisk.vector_disk.VectorDisk#get"
    label: {zh: "读取记录", en: "reads records"}
---
