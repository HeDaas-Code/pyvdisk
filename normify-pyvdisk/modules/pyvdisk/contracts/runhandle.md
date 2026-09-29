---
uid: a0000112
id: pyvdisk.contracts.runhandle
parent: pyvdisk.contracts
name: {zh: "运行句柄", en: "Run Handle"}
description:
  zh: >
      RunHandle：执行平面返回的可观察、可取消句柄；取消不会覆盖终态。
  en: >
      RunHandle: the observable, cancellable handle returned by the execution plane; cancellation never overwrites a terminal state.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 117
    end_line: 155
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.RunHandle"
    description:
      zh: >
          可观察句柄：run_id、状态、结果与错误。
      en: >
          Observable handle carrying run_id, status, result and error.
  - protocol: rpc
    path: "pyvdisk.contracts.RunHandle#complete"
    description:
      zh: >
          将运行标记为成功（已取消则忽略）。
      en: >
          Mark the run succeeded unless it was already cancelled.
  - protocol: rpc
    path: "pyvdisk.contracts.RunHandle#fail"
    description:
      zh: >
          将运行标记为失败（已取消则忽略）。
      en: >
          Mark the run failed unless it was already cancelled.
  - protocol: rpc
    path: "pyvdisk.contracts.RunHandle#cancel"
    description:
      zh: >
          协作式取消尚未完成的运行。
      en: >
          Cooperatively cancel a not-yet-finished run.
  - protocol: rpc
    path: "pyvdisk.contracts.RunHandle#wait"
    description:
      zh: >
          阻塞直到运行结束，并重新抛出其错误。
      en: >
          Block until the run finishes, re-raising its error.
---
