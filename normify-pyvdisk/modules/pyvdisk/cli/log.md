---
uid: a0000c0e
id: pyvdisk.cli.log
parent: pyvdisk.cli
name: {zh: "日志子命令", en: "Log Subcommands"}
description:
  zh: >
      日志盘子命令：流管理、写入、查询、tail、统计、压缩与保留策略。
  en: >
      Log-disk subcommands: stream management, emission, query, tail, statistics, compaction and retention.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 626
    end_line: 674
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_create"
    description:
      zh: >
          创建日志盘。
      en: >
          Create a log disk.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_stream"
    description:
      zh: >
          创建、列举或删除日志流。
      en: >
          Create, list or drop a log stream.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_emit"
    description:
      zh: >
          向流追加事件。
      en: >
          Append an event to a stream.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_query"
    description:
      zh: >
          带过滤条件查询流。
      en: >
          Query a stream with filters.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_tail"
    description:
      zh: >
          打印流的最近事件。
      en: >
          Print the most recent events of a stream.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_stats"
    description:
      zh: >
          打印每流统计。
      en: >
          Print per-stream statistics.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_compact"
    description:
      zh: >
          压缩流。
      en: >
          Compact a stream.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_log_retention"
    description:
      zh: >
          对流派生保留策略。
      en: >
          Enforce retention on a stream.
---
