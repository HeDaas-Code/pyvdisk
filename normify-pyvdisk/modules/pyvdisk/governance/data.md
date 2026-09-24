---
uid: a0000810
id: pyvdisk.governance.data
parent: pyvdisk.governance
name: {zh: "受限数据服务", en: "Scoped Data Services"}
description:
  zh: >
      能力治理的向量与日志半边：按集合与流划分范围，区分读、写、追加与 admin 权限。
      
  en: >
      Vector and log halves of capability governance: collection- and stream-level scoping with read, write, append and admin permissions.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.219Z"
fingerprint: 6e43b5202db42eeca8d389509c7b4cc39ed45eea060f91c8c3a05087de3f820f
source:
  - path: "pyvdisk/infrastructure/capabilities.py"
    line: 83
    end_line: 127
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedVectorNamespace"
    description:
      zh: >
          把每个集合限制在能力范围内的向量适配器。
          
      en: >
          Vector adapter that confines each collection to a capability scope.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedVectorNamespace#_scope"
    description:
      zh: >
          推导集合的范围路径。
          
      en: >
          Derive the scope path of a collection.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedVectorNamespace#create_collection"
    description:
      zh: >
          带权限检查的集合创建。
          
      en: >
          Permission-checked collection creation.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedVectorNamespace#upsert"
    description:
      zh: >
          带权限检查的记录 upsert。
          
      en: >
          Permission-checked record upsert.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedVectorNamespace#search"
    description:
      zh: >
          带权限检查的相似度检索。
          
      en: >
          Permission-checked similarity search.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedLogNamespace"
    description:
      zh: >
          把每个流限制在能力范围内的日志适配器。
          
      en: >
          Log adapter that confines each stream to a capability scope.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedLogNamespace#append"
    description:
      zh: >
          带权限检查的事件追加。
          
      en: >
          Permission-checked event append.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedLogNamespace#enforce_retention"
    description:
      zh: >
          带权限检查的保留策略执行。
          
      en: >
          Permission-checked retention enforcement.
          
deps:
  - kind: call
    to: pyvdisk.storage.vector.records
    from_api: "rpc:pyvdisk.infrastructure.capabilities.ScopedVectorNamespace#upsert"
    to_api: "rpc:pyvdisk.vector_disk.VectorDisk#upsert"
    label: {zh: "委托给向量盘", en: "delegates to vector disk"}
  - kind: call
    to: pyvdisk.storage.log.append
    from_api: "rpc:pyvdisk.infrastructure.capabilities.ScopedLogNamespace#append"
    to_api: "rpc:pyvdisk.log_disk.LogDisk#append"
    label: {zh: "委托给日志盘", en: "delegates to log disk"}
---
