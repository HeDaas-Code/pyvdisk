---
uid: a0000c09
id: pyvdisk.cli.inspect
parent: pyvdisk.cli
name: {zh: "检查子命令", en: "Inspection Subcommands"}
description:
  zh: >
      检查与挂载子命令：stat、tree、mount 与 touch。
  en: >
      Inspection and mounting subcommands: stat, tree, mount and touch.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 255
    end_line: 305
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_stat"
    description:
      zh: >
          打印路径的详细 stat 记录。
      en: >
          Print a detailed stat record for a path.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_tree"
    description:
      zh: >
          打印路径的目录树。
      en: >
          Print the directory tree of a path.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_mount"
    description:
      zh: >
          把磁盘镜像挂载到宿主目录，可选经 FUSE。
      en: >
          Mount a disk image at a host directory, optionally through FUSE.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_touch"
    description:
      zh: >
          创建空文件。
      en: >
          Create an empty file.
---
