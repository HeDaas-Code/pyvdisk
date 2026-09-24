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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: f3bc6b45a520369279ba039c4bf06fb0bfce7e84df609d7d20d81ad24a85dc35
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
