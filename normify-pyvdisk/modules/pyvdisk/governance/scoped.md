---
uid: a0000811
id: pyvdisk.governance.scoped
parent: pyvdisk.governance
name: {zh: "受限容器", en: "Scoped Container"}
description:
  zh: >
      检查点范围限定，以及执行层交给不可信代码的 ScopedDataDisk 对象与工厂。
      
  en: >
      Checkpoint scoping plus the ScopedDataDisk object and factory that execution passes to untrusted code.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.221Z"
fingerprint: 6e43b5202db42eeca8d389509c7b4cc39ed45eea060f91c8c3a05087de3f820f
source:
  - path: "pyvdisk/infrastructure/capabilities.py"
    line: 130
    end_line: 162
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedCheckpointNamespace"
    description:
      zh: >
          把每个键限制在能力集内的检查点适配器。
          
      en: >
          Checkpoint adapter that scopes each key to the capability set.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedDataDisk"
    description:
      zh: >
          交给不可信调用方的单一对象：DataDisk 及其能力上下文。
          
      en: >
          The single object handed to untrusted callers: a DataDisk plus its capability context.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedDataDisk#__enter__"
    description:
      zh: >
          挂载底层容器并返回受限视图。
          
      en: >
          Mount the underlying container and return the scoped view.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedDataDisk#__exit__"
    description:
      zh: >
          上下文退出时关闭底层容器。
          
      en: >
          Close the underlying container on context exit.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.scoped"
    description:
      zh: >
          把一个 DataDisk 包装为单次执行上下文视图的便利工厂。
          
      en: >
          Convenience factory that wraps a DataDisk for one execution context.
          
---
