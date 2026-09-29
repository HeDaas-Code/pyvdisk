---
uid: a0000c06
id: pyvdisk.cli.image
parent: pyvdisk.cli
name: {zh: "镜像子命令", en: "Image Subcommands"}
description:
  zh: >
      镜像生命周期与检查子命令：create、info、status 与列举。
  en: >
      Image lifecycle and inspection subcommands: create, info, status and listing.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 77
    end_line: 152
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_create"
    description:
      zh: >
          按命令行参数创建新的磁盘镜像或卷。
      en: >
          Create a new disk image or volume from CLI arguments.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_info"
    description:
      zh: >
          打印磁盘身份、几何与剩余空间信息。
      en: >
          Print disk identity, geometry and free-space information.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_status"
    description:
      zh: >
          打印紧凑的磁盘状态汇总。
      en: >
          Print a compact disk status summary.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_ls"
    description:
      zh: >
          以 ls 风格输出列举目录。
      en: >
          List a directory with ls-style output.
---
