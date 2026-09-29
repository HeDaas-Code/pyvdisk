---
uid: a0000c08
id: pyvdisk.cli.file-ops
parent: pyvdisk.cli
name: {zh: "文件子命令", en: "File Subcommands"}
description:
  zh: >
      整文件子命令：write、append、copy、move 与宿主导入导出。
  en: >
      Whole-file subcommands: write, append, copy, move and host import/export.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 189
    end_line: 254
apis:
  - protocol: rpc
    path: "pyvdisk.cli.cmd_write"
    description:
      zh: >
          向文件写入数据，内容可内联或来自文件。
      en: >
          Write data into a file, accepting inline or file-sourced content.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_append"
    description:
      zh: >
          向文件追加数据。
      en: >
          Append data to a file.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_cp"
    description:
      zh: >
          在 VFS 内部复制。
      en: >
          Copy inside the VFS.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_mv"
    description:
      zh: >
          在 VFS 内部移动或重命名。
      en: >
          Move or rename inside the VFS.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_import"
    description:
      zh: >
          导入宿主文件或目录树。
      en: >
          Import a host file or tree.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_export"
    description:
      zh: >
          把 VFS 路径导出到宿主。
      en: >
          Export a VFS path to the host.
---
