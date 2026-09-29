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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.260Z"
fingerprint: b93664d4ede6142b0a1f77adbe3592f0ee285c15f7e00e3627f7acae3a5a3431
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
