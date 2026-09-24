---
uid: a0000c0c
id: pyvdisk.cli.drive
parent: pyvdisk.cli
name: {zh: "驱动器子命令", en: "Drive Subcommands"}
description:
  zh: >
      模拟驱动器子命令：scan、mount-all 与卷标管理。
  en: >
      Simulated drive bay subcommands: scan, mount-all and label management.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 493
    end_line: 572
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_scan"
    description:
      zh: >
          扫描宿主目录并报告其中发现的介质。
      en: >
          Scan a host directory and report the media found there.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_mount_all"
    description:
      zh: >
          按卷标挂载全部检测到的盘与卷。
      en: >
          Mount every detected disk and volume by label.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_label"
    description:
      zh: >
          在身份尾标中重置磁盘卷标。
      en: >
          Reassign a disk label in its identity trailer.
---
