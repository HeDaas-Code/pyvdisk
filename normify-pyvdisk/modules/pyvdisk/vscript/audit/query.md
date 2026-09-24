---
uid: a51f4f49
id: pyvdisk.vscript.audit.query
parent: pyvdisk.vscript.audit
tags: [vscript, audit, query, retention]
name: {zh: "审计查询与保留", en: "Audit Query and Retention"}
description:
  zh: >
      审计轨迹的读取侧：按运行/任务/状态/时间筛选记录，并支持显式保留裁剪，使轨迹既可查也可有界，而不是只能追加。
      
  en: >
      Reading side of the audit trail: record selection by run/task/status/time and explicit retention, so a trail can be inspected and bounded instead of only appended to.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.210Z"
fingerprint: e7c398721e85cdb58382b2b377443a1448877191f1be8c698b03443173fc2e4f
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 108
    end_line: 158
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.query_rows"
    description:
      zh: >
          按运行、任务、状态与时间窗筛选审计记录，可要求按最新优先。
          
      en: >
          Selects audit records by run, task, status and time window, optionally newest first.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.retain_rows"
    description:
      zh: >
          按条数与时间裁剪记录列表，返回保留与丢弃两部分。
          
      en: >
          Trims a record list by count and age, returning what was kept and what was dropped.
          
---
