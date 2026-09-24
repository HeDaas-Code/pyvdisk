---
uid: a0000b10
id: pyvdisk.vscript.audit.clock
parent: pyvdisk.vscript.audit
name: {zh: "运行标识", en: "Run Identity"}
description:
  zh: >
      用于填充审计记录的运行标识与耗时测量。
      
  en: >
      Run identity and duration measurement used to fill audit records.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.258Z"
fingerprint: e7c398721e85cdb58382b2b377443a1448877191f1be8c698b03443173fc2e4f
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 99
    end_line: 104
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.new_run_id"
    description:
      zh: >
          生成唯一且按创建时间可排序的 run id。
          
      en: >
          Generate a run id that is unique and sortable by creation time.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.monotonic_ms"
    description:
      zh: >
          自单调起点起经过的毫秒数。
          
      en: >
          Milliseconds elapsed since a monotonic start point.
          
---
