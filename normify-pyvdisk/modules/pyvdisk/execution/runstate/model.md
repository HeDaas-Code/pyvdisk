---
uid: a000090a
id: pyvdisk.execution.runstate.model
parent: pyvdisk.execution.runstate
name: {zh: "运行记录", en: "Run Record"}
description:
  zh: >
      运行记录模型，以及受保护状态迁移使用的乐观并发冲突类型。
  en: >
      Run record model and the optimistic-concurrency conflict type used by guarded transitions.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 38952ffc815f8771c14753783c0e3da128b6877309ee722d94fe8fb43aa54b97
source:
  - path: "pyvdisk/infrastructure/run_state.py"
    line: 7
    end_line: 26
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunStateConflict"
    description:
      zh: >
          版本保护的运行状态迁移被拒时抛出。
      en: >
          Raised when a version-guarded run transition is rejected.
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunRecord"
    description:
      zh: >
          运行记录：id、状态、版本、幂等键与结果/错误引用。
      en: >
          Run record: id, status, version, idempotency key and result or error reference.
  - protocol: rpc
    path: "pyvdisk.infrastructure.run_state.RunRecord#__post_init__"
    description:
      zh: >
          一致地初始化记录版本与状态。
      en: >
          Initialize the record version and status consistently.
---
