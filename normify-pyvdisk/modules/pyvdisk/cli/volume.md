---
uid: a0000c0b
id: pyvdisk.cli.volume
parent: pyvdisk.cli
name: {zh: "卷子命令", en: "Volume Subcommands"}
description:
  zh: >
      卷子命令：创建、状态与在线镜像维护。
  en: >
      Volume subcommands covering creation, status and online mirror maintenance.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 408
    end_line: 492
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vol_create"
    description:
      zh: >
          创建多盘卷。
      en: >
          Create a multi-disk volume.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vol_status"
    description:
      zh: >
          打印卷模式、成员与健康状况。
      en: >
          Print volume mode, members and health.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vol_format"
    description:
      zh: >
          格式化已有卷。
      en: >
          Format an existing volume.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vol_add"
    description:
      zh: >
          在线新增镜像成员。
      en: >
          Add a mirror member online.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vol_remove"
    description:
      zh: >
          在线移除镜像成员。
      en: >
          Remove a mirror member online.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vol_resync"
    description:
      zh: >
          重新同步镜像成员。
      en: >
          Resynchronize mirror members.
---
