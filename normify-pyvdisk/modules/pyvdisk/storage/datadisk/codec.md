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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
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
