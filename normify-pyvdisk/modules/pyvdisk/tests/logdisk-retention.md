---
uid: a0000e13
id: pyvdisk.tests.logdisk-retention
parent: pyvdisk.tests
name: {zh: "日志保留用例", en: "Log Retention Tests"}
description:
  zh: >
      验证保留策略不会删除消费者尚未确认的事件。
      
  en: >
      Verifies retention never drops an event a consumer has not yet acknowledged.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 0ba50a397b61ec091c3b0a00bc29c99511bb368b54829ddf1b7e5cb23c1afc4a
source:
  - path: "tests/test_logdisk_retention_event_ids.py"
apis:
  - protocol: rpc
    path: "tests/test_logdisk_retention_event_ids.py"
    description:
      zh: >
          保留策略遵守事件 id 边界。
          
      en: >
          Retention honours event id boundaries.
          
deps:
  - kind: call
    to: pyvdisk.storage.log.retention
    to_api: "rpc:pyvdisk.log_disk.LogDisk#enforce_retention"
    label: {zh: "验证保留策略", en: "verifies retention"}
---
