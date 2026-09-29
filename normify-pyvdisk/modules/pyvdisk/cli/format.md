---
uid: a0000c04
id: pyvdisk.cli.format
parent: pyvdisk.cli
name: {zh: "CLI 格式化", en: "CLI Formatting"}
description:
  zh: >
      各子命令共用的 CLI 格式化与解析辅助。
  en: >
      CLI formatting and parsing helpers shared by every subcommand.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 24
    end_line: 64
apis:
  - protocol: rpc
    path: "pyvdisk.cli._parse_size"
    description:
      zh: >
          把带单位后缀的尺寸字符串解析为字节数。
      en: >
          Parse size strings with unit suffixes into bytes.
  - protocol: rpc
    path: "pyvdisk.cli._type_str"
    description:
      zh: >
          把 inode 类型号渲染为 ls 风格字符。
      en: >
          Render an inode type number as its ls-style letter.
  - protocol: rpc
    path: "pyvdisk.cli._human_size"
    description:
      zh: >
          把字节数格式化为人类可读。
      en: >
          Format a byte count for humans.
  - protocol: rpc
    path: "pyvdisk.cli._add_cred_args"
    description:
      zh: >
          为子解析器添加 uid/gid 凭据选项。
      en: >
          Add uid/gid credential options to a subparser.
---
