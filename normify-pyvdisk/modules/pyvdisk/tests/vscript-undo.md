---
uid: c9d0c415
id: pyvdisk.tests.vscript-undo
parent: pyvdisk.tests
tags: [tests, vscript, undo]
name: {zh: "撤销用例", en: "Undo Tests"}
description:
  zh: >
      撤销用例：每个 fs 动词在生效前记账、大正文落盘、restore_tree 与崩溃后遗留快照的清理。
      
  en: >
      Undo tests: every fs verb journalled before it mutates, large bodies spilled to the transaction area, restore_tree and orphan-spill cleanup after a crash.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.214Z"
fingerprint: ac95991d897d56633679357d40f3e5463cee13f38c4e2730da86fb757cd72d7f
source:
  - path: "tests/test_vscript_undo.py"
    line: 1
    end_line: 373
apis:
  - protocol: rpc
    path: "tests/test_vscript_undo.py"
    description:
      zh: >
          撤销词汇表、落盘、崩溃恢复，以及词汇与动词覆盖校验的 22 个用例。
          
      en: >
          22 cases over the undo vocabulary, spilling, crash recovery and the vocabulary-vs-verb coverage check.
          
deps:
  - kind: call
    to: pyvdisk.vscript.undo
    from_api: "rpc:tests/test_vscript_undo.py"
    to_api: "rpc:pyvdisk.vscript.undo.apply_undo"
    label: {zh: "验证撤销解释器", en: "exercises undo interpreter"}
---
