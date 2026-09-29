---
uid: a0000e12
id: pyvdisk.tests.logdisk-compact
parent: pyvdisk.tests
name: {zh: "日志压缩用例", en: "Log Compaction Tests"}
description:
  zh: >
      守住压缩绝不可违反的性质：减少存储不得改变可观测的流状态。
      
  en: >
      Guards the property compaction must never violate: reducing storage must not change observable stream state.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 7a9187ee29732e657f68810200e105353ea441bd926fbabc8811b387047a8a9d
source:
  - path: "tests/test_logdisk_compact_preserves_state.py"
apis:
  - protocol: rpc
    path: "tests/test_logdisk_compact_preserves_state.py"
    description:
      zh: >
          压缩保留流与状态元数据。
          
      en: >
          Compaction preserves stream and state metadata.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.retention
    to_api: "rpc:pyvdisk.log_disk.LogDisk#compact"
    label: {zh: "验证压缩", en: "verifies compaction"}
---
