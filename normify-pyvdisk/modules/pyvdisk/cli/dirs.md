---
uid: a0000c07
id: pyvdisk.cli.dirs
parent: pyvdisk.cli
name: {zh: "目录子命令", en: "Directory Subcommands"}
description:
  zh: >
      目录与删除子命令，语义与对应文件系统操作一致。
  en: >
      Directory and deletion subcommands, with the same semantics as their filesystem counterparts.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 153
    end_line: 188
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_mkdir"
    description:
      zh: >
          创建单个目录。
      en: >
          Create one directory.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_rmdir"
    description:
      zh: >
          删除空目录。
      en: >
          Remove an empty directory.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_rm"
    description:
      zh: >
          删除文件或目录树。
      en: >
          Remove a file or directory tree.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_cat"
    description:
      zh: >
          把文件内容输出到标准输出。
      en: >
          Print a file to standard output.
---
