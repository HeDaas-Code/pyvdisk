---
uid: a0000334
id: pyvdisk.storage.vector.flat-index
parent: pyvdisk.storage.vector
tags: [zero-dependency, vector]
name: {zh: "扁平索引后端", en: "Flat Index Backend"}
description:
  zh: >
      纯 Python 精确索引，接口形状对齐 hnswlib，VectorDisk 因此可以直接回退而不必在调用点分支。查询是 O(n) 且向量常驻内存：适合中小集合，不是大规模下 HNSW 的替代品。
  en: >
      A pure-Python exact index that mirrors hnswlib's calling shape, so VectorDisk can fall back to it without branching. Query is O(n) and the vectors stay in memory: correct for small and medium collections, not a replacement for HNSW at scale.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: c2a8e20da7599125065676cf6a3cea638d1a8108df234b9873b098dbfffb547d
source:
  - path: "pyvdisk/vector_index.py"
    line: 38
    end_line: 47
  - path: "pyvdisk/vector_index.py"
    line: 51
    end_line: 83
  - path: "pyvdisk/vector_index.py"
    line: 169
    end_line: 251
apis:
  - protocol: rpc
    path: "vector_index:distance"
    description:
      zh: >
          按 hnswlib 的约定计算距离，两种后端在调用点可直接互换：cosine = 1 - 相似度，l2 = 平方欧氏距离，ip = 1 - 点积。
      en: >
          Distance in the convention hnswlib uses, so the two backends are interchangeable at the call site: cosine = 1 - similarity, l2 = squared euclidean, ip = 1 - dot product.
  - protocol: rpc
    path: "vector_index:read_kind"
    description:
      zh: >
          从索引文件读出写入方标识：是 hnswlib 写的还是 flat 后端写的，不需要解析其余内容。
      en: >
          Read the writer's tag from an index file: whether it was written by hnswlib or by the flat backend, without parsing the rest.
  - protocol: rpc
    path: "vector_index:serialize"
    description:
      zh: >
          序列化为 flat 格式：8 字节魔数、空间与维度，然后是标签与 float32 向量。
      en: >
          Serialise to the flat format: an 8-byte magic, the space and dimension, then labels and float32 vectors.
  - protocol: rpc
    path: "vector_index:deserialize"
    description:
      zh: >
          解析 flat 索引；内容被截断或根本不是该格式时报错，而不是当成正确数据读下去。
      en: >
          Parse a flat index, rejecting a truncated or foreign payload instead of misreading it.
  - protocol: rpc
    path: "vector_index:serialize_from_backend"
    description:
      zh: >
          序列化任一后端的索引：flat 索引直接写自己，hnswlib 索引走它自己的 save_index 落到临时文件，需要负责清理。
      en: >
          Serialise an index of either backend: a flat index writes itself, an hnswlib index goes through its own save_index into a temporary file that must be unlinked.
  - protocol: rpc
    path: "vector_index:FlatIndex.add_item"
    description:
      zh: >
          写入一条带标签的向量。维度与索引不一致时报错，维度尚未确定的空索引也拒绝写入。
      en: >
          Add a labelled vector. Rejects a vector whose dimension disagrees with the index, and refuses a fresh index whose dimension was never set.
  - protocol: rpc
    path: "vector_index:FlatIndex.knn_query"
    description:
      zh: >
          精确 k 近邻搜索。距离相同时按标签排序，保证多次运行结果稳定；可选断言用于筛选候选记录。
      en: >
          Exact k-nearest search. Ties break on the label so results are stable across runs, and an optional predicate filters the candidate records.
---
