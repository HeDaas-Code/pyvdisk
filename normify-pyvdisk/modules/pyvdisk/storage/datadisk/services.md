---
uid: a000080b
id: pyvdisk.storage.datadisk.services
parent: pyvdisk.storage.datadisk
name: {zh: "服务命名空间", en: "Service Namespaces"}
description:
  zh: >
      向量与日志命名空间：透传到各自磁盘，同时作为一等事务参与者。
      
  en: >
      Vector and log namespaces that pass through to their disks while remaining first-class transaction participants.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.227Z"
fingerprint: 9e43dcc0192ae7fcb043dfd6e12b09e42ba36fa2b8b01c445b2e84a45d351d93
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 344
    end_line: 405
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.VectorNamespace"
    description:
      zh: >
          参与元数据事务的透传向量命名空间。
          
      en: >
          Read-through vector namespace participating in metadata transactions.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.LogNamespace"
    description:
      zh: >
          参与元数据事务的透传事件日志命名空间。
          
      en: >
          Read-through event-log namespace participating in metadata transactions.
          
deps:
  - kind: call
    to: pyvdisk.storage.vector.records
    from_api: "rpc:pyvdisk.infrastructure.disk.VectorNamespace"
    to_api: "rpc:pyvdisk.vector_disk.VectorDisk#upsert"
    label: {zh: "包装向量盘", en: "wraps vector disk"}
  - kind: call
    to: pyvdisk.storage.log.append
    from_api: "rpc:pyvdisk.infrastructure.disk.LogNamespace"
    to_api: "rpc:pyvdisk.log_disk.LogDisk#append"
    label: {zh: "包装日志盘", en: "wraps log disk"}
---
