---
uid: afb559b5
id: pyvdisk.tests.participant-compensation
parent: pyvdisk.tests
tags: [tests, transaction, acid]
name: {zh: "参与者补偿用例", en: "Participant Compensation Tests"}
description:
  zh: >
      参与者补偿用例：持久化写前补偿、进程内 abort 的逆序分发、跨挂载的幂等重复补偿。
      
  en: >
      Participant compensation tests: durable write-ahead compensation, reverse-order in-process abort dispatch, idempotent re-compensation across mounts.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.212Z"
fingerprint: 64c934ebf5a17e261b860af5ab6856ead8c9072cf123163c17ba128406b349e0
source:
  - path: "tests/test_participant_compensation.py"
    line: 1
    end_line: 358
apis:
  - protocol: rpc
    path: "tests/test_participant_compensation.py"
    description:
      zh: >
          参与者登记、持久补偿日志与崩溃矩阵恢复的 38 个用例。
          
      en: >
          38 cases over participant enlistment, the durable compensation log and crash-matrix recovery.
          
deps:
  - kind: call
    to: pyvdisk.storage.datadisk.tx-lifecycle
    from_api: "rpc:tests/test_participant_compensation.py"
    to_api: "rpc:pyvdisk.infrastructure.disk.MetadataTransaction#abort"
    label: {zh: "验证事务补偿", en: "exercises tx compensation"}
---
