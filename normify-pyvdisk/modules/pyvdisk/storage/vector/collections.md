---
uid: a0000602
id: pyvdisk.storage.vector.collections
parent: pyvdisk.storage.vector
name: {zh: "集合目录", en: "Collections"}
description:
  zh: >
      集合目录：按维度与度量创建、带配置列举，以及连同每集合 HNSW 索引一起删除。
      
  en: >
      Collection catalogue: create with dimension and metric, list with configuration, and drop along with the per-collection HNSW index.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: ee801e56c4d436543de323aa02bb0c3a4e78339ef28b5c1ec180ad68cee817b0
source:
  - path: "pyvdisk/vector_disk.py"
    line: 129
    end_line: 163
apis:
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#create_collection"
    description:
      zh: >
          以固定维度与度量创建具名集合。
          
      en: >
          Create a named collection with a fixed dimension and metric.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#list_collections"
    description:
      zh: >
          列出集合名称及其配置。
          
      en: >
          List the collection names with their configuration.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#drop_collection"
    description:
      zh: >
          删除集合及其索引文件。
          
      en: >
          Drop a collection and its index files.
          
---
