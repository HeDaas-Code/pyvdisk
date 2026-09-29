---
uid: a0000904
id: pyvdisk.execution.service.submit
parent: pyvdisk.execution.service
name: {zh: "提交与取消", en: "Submit and Cancel"}
description:
  zh: >
      ExecutionPlane 协议的实现：submit、阻塞式 run 与取消。
      
  en: >
      The ExecutionPlane protocol implementation: submit, blocking run and cancellation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.308Z"
fingerprint: 4152ec61e453494829e848f89f2834faa980e43e4bb670d7b0814b68d3187b61
source:
  - path: "pyvdisk/execution.py"
    line: 253
    end_line: 284
apis:
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#submit"
    description:
      zh: >
          提交操作并立即返回 RunHandle。
          
      en: >
          Submit an operation and return a RunHandle immediately.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#run"
    description:
      zh: >
          提交操作并阻塞至完成。
          
      en: >
          Submit an operation and block until it finishes.
          
  - protocol: rpc
    path: "pyvdisk.execution.ExecutionService#cancel"
    description:
      zh: >
          协作式取消已提交的操作。
          
      en: >
          Cooperatively cancel a submitted operation.
          
deps:
  - kind: call
    to: pyvdisk.contracts.runhandle
    from_api: "rpc:pyvdisk.execution.ExecutionService#submit"
    to_api: "rpc:pyvdisk.contracts.RunHandle"
    label: {zh: "返回句柄", en: "returns handle"}
---
