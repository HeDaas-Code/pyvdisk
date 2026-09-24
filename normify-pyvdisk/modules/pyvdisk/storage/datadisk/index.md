---
uid: a000030d
id: pyvdisk.storage.datadisk
parent: pyvdisk.storage
tags: [acid, transaction]
name: {zh: "DataDisk 容器", en: "DataDisk Container"}
description:
  zh: >
      统一 DataDisk 容器：一个挂载的 VFS 加上 FS/向量/日志命名空间服务，带撤销日志的元数据事务、WAL 与重挂载恢复。
  en: >
      Unified DataDisk container: one mounted VFS plus namespaced FS/vector/log services, a metadata transaction with undo journal, WAL and remount recovery.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
source:
  - path: "pyvdisk/infrastructure/disk.py"
---
