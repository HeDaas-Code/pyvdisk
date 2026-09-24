---
uid: a0000604
id: pyvdisk.storage.vector.search
parent: pyvdisk.storage.vector
name: {zh: "向量检索", en: "Vector Search"}
description:
  zh: >
      索引构建、加载与查询。后端在加载时由文件魔数决定：装了 hnswlib 就用它，否则用内置 flat 索引。以一次改名发布，并发读方看到的要么是旧索引要么是新索引。
  en: >
      Index construction, loading and query. The backend is chosen at load time from the file's magic tag: hnswlib when installed, the built-in flat index otherwise. Published with a single rename, so a concurrent reader sees either the old index or the new one.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: ee801e56c4d436543de323aa02bb0c3a4e78339ef28b5c1ec180ad68cee817b0
source:
  - path: "pyvdisk/vector_disk.py"
    line: 223
    end_line: 267
apis:
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#_rebuild_index"
    description:
      zh: >
          由记录重建索引，并以一次改名原子发布，读方不会看到写了一半的索引。
      en: >
          Rebuild the index from the records and publish it with one rename, so a reader never sees a half-written index.
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#_load_index"
    description:
      zh: >
          加载集合索引。由文件魔数决定路径：flat 直接解析，hnswlib 索引经 hnswlib 加载，缺 hnswlib 时回退为按记录重建的精确索引。
      en: >
          Load the collection index. The file's magic decides how: flat parses directly, hnswlib loads through hnswlib, and a missing hnswlib falls back to an exact index over the records.
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#search"
    description:
      zh: >
          最近邻检索，可带元数据过滤。
      en: >
          Nearest-neighbour search with an optional metadata filter.
deps:
  - kind: call
    to: pyvdisk.storage.vector.flat-index
    from_api: "rpc:pyvdisk.vector_disk.VectorDisk#_load_index"
    label: {zh: "后端回退", en: "backend fallback"}
---
