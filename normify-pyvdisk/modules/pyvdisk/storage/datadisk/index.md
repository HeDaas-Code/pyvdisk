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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.225Z"
fingerprint: 9e43dcc0192ae7fcb043dfd6e12b09e42ba36fa2b8b01c445b2e84a45d351d93
source:
  - path: "pyvdisk/infrastructure/disk.py"
---
