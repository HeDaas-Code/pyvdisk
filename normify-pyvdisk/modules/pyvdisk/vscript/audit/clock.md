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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: e6e0c4f6567b6878156a09474961840eaaf3271a6f54be1751ac87c88fbbcebc
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
