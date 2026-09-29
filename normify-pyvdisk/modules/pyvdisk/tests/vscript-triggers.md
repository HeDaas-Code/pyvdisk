---
uid: 35b668fb
id: pyvdisk.tests.vscript-triggers
parent: pyvdisk.tests
tags: [tests, vscript, triggers]
name: {zh: "触发器用例", en: "Trigger Tests"}
description:
  zh: >
      触发器用例：单调水位线排序（此前用随机事件 id 作文本比较会静默丢事件）、注册时空 pattern/stream 的拒绝，以及 poll_once 行为。
      
  en: >
      Trigger tests: monotonic watermark ordering (a random event id used as a text watermark silently dropped events), empty pattern/stream rejection at registration, and poll_once behaviour.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.213Z"
fingerprint: b1079ad935b3695ebcb3c4682ab7849a80d348c1157e0634d225057496340185
source:
  - path: "tests/test_vscript_triggers.py"
    line: 1
    end_line: 282
apis:
  - protocol: rpc
    path: "tests/test_vscript_triggers.py"
    description:
      zh: >
          文件与日志触发器、其水位线与注册规则的 19 个用例。
          
      en: >
          19 cases over file and log triggers, their watermarks and their registration rules.
          
deps:
  - kind: call
    to: pyvdisk.vscript.triggers.daemon
    from_api: "rpc:tests/test_vscript_triggers.py"
    to_api: "rpc:pyvdisk.vscript.triggers.SchedulerDaemon#poll_once"
    label: {zh: "验证触发器守护进程", en: "exercises trigger daemon"}
---
