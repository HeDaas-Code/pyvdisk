---
uid: a0000c03
id: pyvdisk.vscript.cli.parser
parent: pyvdisk.vscript.cli
name: {zh: "VScript 参数注册", en: "VScript Parser Hook"}
description:
  zh: >
      把 VScript 接口挂到 pyvdisk 主 CLI 上的 argparse 注册。
  en: >
      argparse registration that grafts the VScript surface onto the main pyvdisk CLI.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8804f57427cc348f66a87e62a16cb43057e614c4d7ea12f01e4d8c384d5b716f
source:
  - path: "pyvdisk/vscript/cli.py"
    line: 152
    end_line: 159
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.cli.add_parser"
    description:
      zh: >
          挂载 vscript 子解析器及其 check、run、run-disk 与 repl 选项。
      en: >
          Attach the vscript subparser with its check, run, run-disk and repl options.
---
