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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 265
    end_line: 299
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
