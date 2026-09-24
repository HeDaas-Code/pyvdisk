---
uid: a0000111
id: pyvdisk.contracts.execution
parent: pyvdisk.contracts
name: {zh: "执行上下文", en: "Execution Context"}
description:
  zh: >
      ExecutionContext：交给单次二层执行的依赖与策略信封。
  en: >
      ExecutionContext: the dependency and policy envelope handed to one layer-2 execution.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 99
    end_line: 114
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.ExecutionContext"
    description:
      zh: >
          执行依赖与策略：run_id、能力授权、持久性、存储句柄与截止时间。
      en: >
          Execution dependencies and policy: run_id, capability grants, durability, stores, deadline.
  - protocol: rpc
    path: "pyvdisk.contracts.ExecutionContext#require"
    description:
      zh: >
          没有任何授权允许该权限时抛出 PermissionError。
      en: >
          Raise PermissionError unless some grant allows the permission.
  - protocol: rpc
    path: "pyvdisk.contracts.ExecutionContext#expired"
    description:
      zh: >
          判断执行截止时间是否已过。
      en: >
          Report whether the execution deadline has passed.
---
