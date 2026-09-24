---
uid: a0000807
id: pyvdisk.storage.datadisk.codec
parent: pyvdisk.storage.datadisk
name: {zh: "元数据编解码", en: "Metadata Codec"}
description:
  zh: >
      DataDisk 的值编码与错误词表，供事务、manifest 与命名空间层共用。
      
  en: >
      DataDisk value encoding and error vocabulary shared by the transaction, manifest and namespace layers.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.226Z"
fingerprint: 9e43dcc0192ae7fcb043dfd6e12b09e42ba36fa2b8b01c445b2e84a45d351d93
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 13
    end_line: 19
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDiskError"
    description:
      zh: >
          DataDisk 容器的运行时错误基类。
          
      en: >
          Base runtime error for the DataDisk container.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk._Missing"
    description:
      zh: >
          在元数据事务中标记值被删除的哨兵。
          
      en: >
          Sentinel that marks a value as deleted inside the metadata transaction.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk._json"
    description:
      zh: >
          元数据值的规范 JSON 编码。
          
      en: >
          Canonical JSON encoding for metadata values.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk._enc"
    description:
      zh: >
          manifest 与事务日志用来内嵌值的 base64 包装。
          
      en: >
          Base64 wrapper the manifest and transaction journal use to embed values.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk._dec"
    description:
      zh: >
          base64 包装的逆操作。
          
      en: >
          Reverse of the base64 wrapper.
          
---
