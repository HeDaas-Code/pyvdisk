---
uid: a0000a0a
id: pyvdisk.vscript.cron
parent: pyvdisk.vscript
name: {zh: "Cron 表达式", en: "Cron Expressions"}
description:
  zh: >
      定时触发器所需的 cron 支持：字段解析、匹配与下次触发计算。
      
  en: >
      Cron support for scheduled triggers: field parsing, matching and next-fire computation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:10:41.894Z"
fingerprint: 2c377873cb40f385dd5256018381f5c9b79dcd3b26f5e1761235b6b8de0804a0
source:
  - path: "pyvdisk/vscript/cron.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.cron.CronError"
    description:
      zh: >
          cron 表达式非法时抛出。
          
      en: >
          Raised for malformed cron expressions.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cron.CronExpression"
    description:
      zh: >
          已解析的五字段 cron 表达式，支持范围与步长。
          
      en: >
          Parsed five-field cron expression with range and step support.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cron.CronExpression#matches"
    description:
      zh: >
          判断某值是否匹配该表达式。
          
      en: >
          Test whether a value matches the expression.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cron.CronExpression#next_after"
    description:
      zh: >
          计算给定时间之后的下一个匹配时间戳。
          
      en: >
          Compute the next matching timestamp after a given one.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cron.cron"
    description:
      zh: >
          解析 cron 表达式字符串。
          
      en: >
          Parse a cron expression string.
          
---
