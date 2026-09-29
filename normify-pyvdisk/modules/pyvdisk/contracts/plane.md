---
uid: a0000113
id: pyvdisk.contracts.plane
parent: pyvdisk.contracts
name: {zh: "执行平面协议", en: "Execution Plane"}
description:
  zh: >
      ExecutionPlane 协议：每个执行后端都必须暴露的唯一 submit 入口。
  en: >
      ExecutionPlane protocol: the single submit entry point every execution backend must expose.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 158
    end_line: 162
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.ExecutionPlane#submit"
    description:
      zh: >
          带执行上下文提交操作并返回 RunHandle。
      en: >
          Submit an operation with an execution context and return a RunHandle.
---
