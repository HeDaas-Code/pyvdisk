---
uid: a0000c10
id: pyvdisk.cli.main
parent: pyvdisk.cli
name: {zh: "CLI 入口", en: "CLI Entry Point"}
description:
  zh: >
      CLI 入口：把错误映射为退出码，以及 python -m pyvdisk 钩子。
      
  en: >
      The CLI entry point: error mapping to exit codes, and the python -m pyvdisk hook.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:26:30.912Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 950
    end_line: 966
apis:
  - protocol: rpc
    path: "pyvdisk.cli.main"
    description:
      zh: >
          解析参数、分发子命令并把错误转为退出码。
      en: >
          Parse arguments, dispatch the subcommand and translate errors into exit codes.
---
