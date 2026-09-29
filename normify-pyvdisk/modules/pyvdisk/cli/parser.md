---
uid: a0000c0f
id: pyvdisk.cli.parser
parent: pyvdisk.cli
name: {zh: "参数解析器", en: "Argument Parser"}
description:
  zh: >
      参数解析器定义：全部子命令、各自选项与共享的镜像参数组。
      
  en: >
      The argument parser definition: every subcommand, its options and the shared image argument group.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 675
    end_line: 949
apis:
  - protocol: rpc
    path: "pyvdisk.cli.build_parser"
    description:
      zh: >
          构建完整 argparse 树，含嵌套镜像参数与 vscript 钩子。
          
      en: >
          Build the full argparse tree, including nested image arguments and the vscript hook.
          
deps:
  - kind: call
    to: pyvdisk.vscript.cli.parser
    from_api: "rpc:pyvdisk.cli.build_parser"
    to_api: "rpc:pyvdisk.vscript.cli.add_parser"
    label: {zh: "添加 vscript 子解析器", en: "adds vscript parser"}
---
