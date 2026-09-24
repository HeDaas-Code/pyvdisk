---
uid: a0000c0a
id: pyvdisk.cli.admin
parent: pyvdisk.cli
name: {zh: "管理子命令", en: "Admin Subcommands"}
description:
  zh: >
      管理类子命令：格式化、链接、属性、空间统计、fsck 与扩容。
  en: >
      Administrative subcommands: format, links, attributes, space accounting, fsck and resize.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 306
    end_line: 407
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_format"
    description:
      zh: >
          格式化镜像，可选强制重建。
      en: >
          Format an image, optionally forcing re-creation.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_ln"
    description:
      zh: >
          创建硬链接或符号链接。
      en: >
          Create a hard or symbolic link.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_chmod"
    description:
      zh: >
          修改模式位。
      en: >
          Change mode bits.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_chown"
    description:
      zh: >
          修改属主。
      en: >
          Change ownership.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_df"
    description:
      zh: >
          打印文件系统空间使用。
      en: >
          Print filesystem space usage.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_du"
    description:
      zh: >
          打印子树的递归占用。
      en: >
          Print recursive disk usage of a subtree.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_fsck"
    description:
      zh: >
          运行一致性检查，可选修复。
      en: >
          Run a consistency check, optionally repairing.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_resize"
    description:
      zh: >
          就地扩容镜像。
      en: >
          Grow an image in place.
---
