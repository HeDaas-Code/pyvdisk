---
uid: a0000e17
id: pyvdisk.tests.submit-conflict
parent: pyvdisk.tests
name: {zh: "提交冲突用例", en: "Submit Conflict Tests"}
description:
  zh: >
      交互用例：提交时的版本冲突不得留下写一半的 VFS 变更。
      
  en: >
      Interaction test: a version conflict on submit must not leave a half-written VFS change behind.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 5b380c22c98ad59d559a3c9b684cc8c33bbefabf64a9196685158a3e9870dcc4
source:
  - path: "tests/test_submit_conflict_and_atomic_vfs.py"
apis:
  - protocol: rpc
    path: "tests/test_submit_conflict_and_atomic_vfs.py"
    description:
      zh: >
          提交冲突解决与 VFS 原子保存的组合用例。
          
      en: >
          Submit conflict resolution combined with atomic VFS save.
          
deps:
  - kind: call
    to: pyvdisk.execution.runstate.store
    to_api: "rpc:pyvdisk.infrastructure.run_state.RunStateStore#transition"
    label: {zh: "验证冲突处理", en: "verifies conflict handling"}
---
