---
uid: 1cbfc35e
id: pyvdisk.tests.vscript-cron
parent: pyvdisk.tests
tags: [tests, vscript, cron]
name: {zh: "Cron 用例", en: "Cron Tests"}
description:
  zh: >
      Cron 用例：字段解析、日/星期并集语义、步长与区间写法，以及下次触发时间计算。
      
  en: >
      Cron tests: field parsing, DOM/DOW union semantics, step and range forms, and next-fire calculation.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.213Z"
fingerprint: 2fbf8277488694b433afe2cca201c9ecdd57759b921b02f8a91484dfe7f331e2
source:
  - path: "tests/test_vscript_cron.py"
    line: 1
    end_line: 109
apis:
  - protocol: rpc
    path: "tests/test_vscript_cron.py"
    description:
      zh: >
          cron 字段解析、匹配与下次触发计算的 29 个用例。
          
      en: >
          29 cases over cron field parsing, matching and next-fire computation.
          
deps:
  - kind: call
    to: pyvdisk.vscript.cron
    from_api: "rpc:tests/test_vscript_cron.py"
    to_api: "rpc:pyvdisk.vscript.cron.CronExpression#next_after"
    label: {zh: "验证 cron 表达式", en: "exercises cron expressions"}
---
