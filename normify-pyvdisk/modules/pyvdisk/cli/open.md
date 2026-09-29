---
uid: a0000c05
id: pyvdisk.cli.open
parent: pyvdisk.cli
name: {zh: "CLI 打开 VFS", en: "CLI VFS Open"}
description:
  zh: >
      每个文件系统子命令获取已挂载 VFS 的唯一入口。
      
  en: >
      The single entry point every filesystem subcommand uses to obtain a mounted VFS.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.024Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 65
    end_line: 75
apis:
  - protocol: rpc
    path: "pyvdisk.cli._open_vfs"
    description:
      zh: >
          按命令行参数打开 VFS，处理凭据与卷成员。
          
      en: >
          Open the VFS named by CLI arguments, resolving credentials and volume membership.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.open
    from_api: "rpc:pyvdisk.cli._open_vfs"
    to_api: "rpc:pyvdisk.vfs.VFS"
    label: {zh: "打开 VFS", en: "opens VFS"}
---
