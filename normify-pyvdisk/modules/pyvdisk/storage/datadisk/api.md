---
uid: a000080d
id: pyvdisk.storage.datadisk.api
parent: pyvdisk.storage.datadisk
name: {zh: "DataDisk 接口", en: "DataDisk Interface"}
description:
  zh: >
      容器生命周期与面向调用方的接口：挂载、manifest、事务、元数据访问与能力受限视图。
      
  en: >
      Container lifecycle and the caller-facing surface: mount, manifest, transactions, metadata access and capability-scoped views.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.225Z"
fingerprint: 9e43dcc0192ae7fcb043dfd6e12b09e42ba36fa2b8b01c445b2e84a45d351d93
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 566
    end_line: 609
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#mount"
    description:
      zh: >
          挂载容器及其三个命名空间。
          
      en: >
          Mount the container and its three namespaces.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#close"
    description:
      zh: >
          关闭全部命名空间与底层 VFS。
          
      en: >
          Close all namespaces and the underlying VFS.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#mounted"
    description:
      zh: >
          报告容器当前是否已挂载。
          
      en: >
          Report whether the container is currently mounted.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#manifest"
    description:
      zh: >
          返回描述命名空间与元数据根的容器 manifest。
          
      en: >
          Return the container manifest describing namespaces and metadata root.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#transaction"
    description:
      zh: >
          在容器上开启元数据事务。
          
      en: >
          Open a metadata transaction over the container.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#get_metadata"
    description:
      zh: >
          读取一个元数据键。
          
      en: >
          Read one metadata key.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#set_metadata"
    description:
      zh: >
          在事务内写入一个元数据键。
          
      en: >
          Write one metadata key inside a transaction.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.DataDisk#scoped"
    description:
      zh: >
          把容器包装为面向执行上下文的能力受限视图。
          
      en: >
          Wrap the container in a capability-scoped view for an execution context.
          
deps:
  - kind: call
    to: pyvdisk.governance.scoped
    from_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#scoped"
    to_api: "rpc:pyvdisk.infrastructure.capabilities.ScopedDataDisk"
    label: {zh: "构建受限视图", en: "builds scoped view"}
  - kind: call
    to: pyvdisk.storage.datadisk.tx-lifecycle
    from_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#transaction"
    to_api: "rpc:pyvdisk.infrastructure.disk.MetadataTransaction#commit"
    label: {zh: "开启事务", en: "opens transaction"}
---
