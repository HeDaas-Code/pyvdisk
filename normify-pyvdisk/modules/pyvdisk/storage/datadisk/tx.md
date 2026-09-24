---
uid: a0000808
id: pyvdisk.storage.datadisk.tx
parent: pyvdisk.storage.datadisk
name: {zh: "元数据事务", en: "Metadata Transaction"}
description:
  zh: >
      元数据事务核心：参与者协议、暂存写入，以及使命名空间变更可回滚的撤销日志。
  en: >
      Metadata transaction core: participant protocol, staged writes and the undo journal that makes namespace mutations reversible.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 21
    end_line: 107
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.TransactionParticipant"
    description:
      zh: >
          命名空间加入元数据事务所实现的协议。
      en: >
          Protocol a namespace implements to join a metadata transaction.
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction"
    description:
      zh: >
          两阶段元数据事务：暂存键值、招募参与者并为撤销记录文件系统意图。
      en: >
          Two-phase metadata transaction staging keys, enlisting participants and recording filesystem intents for undo.
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#set"
    description:
      zh: >
          暂存一次元数据键写入。
      en: >
          Stage a metadata key write.
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#delete"
    description:
      zh: >
          暂存一次元数据键删除。
      en: >
          Stage a metadata key deletion.
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#enlist"
    description:
      zh: >
          招募命名空间参与者，可选带意图。
      en: >
          Enlist a namespace participant, optionally with an intent.
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.MetadataTransaction#intent"
    description:
      zh: >
          声明操作用意图，用于冲突检测与重试。
      en: >
          Declare an operation intent used for conflict detection and retry.
---
