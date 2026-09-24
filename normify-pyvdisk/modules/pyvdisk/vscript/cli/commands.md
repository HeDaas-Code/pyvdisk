---
uid: a0000c01
id: pyvdisk.vscript.cli.commands
parent: pyvdisk.vscript.cli
name: {zh: "VScript 命令", en: "VScript Commands"}
description:
  zh: >
      VScript 命令接口：参数解析、挂载授权，以及 check 与 run 入口。
      
  en: >
      VScript command surface: argument parsing, mount authorization and the check and run entry points.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 8804f57427cc348f66a87e62a16cb43057e614c4d7ea12f01e4d8c384d5b716f
source:
  - path: "pyvdisk/vscript/cli.py"
    line: 7
    end_line: 46
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.cli._pairs"
    description:
      zh: >
          把重复的 key=value 命令行参数解析为字典。
          
      en: >
          Parse repeated key=value CLI arguments into a dictionary.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cli._mounts"
    description:
      zh: >
          从 name=path=permissions 参数构建挂载句柄。
          
      en: >
          Build mount handles from name=path=permissions arguments.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cli.command"
    description:
      zh: >
          分发 check、run 与 run-disk 子命令。
          
      en: >
          Dispatch the check, run and run-disk subcommands.
          
deps:
  - kind: call
    to: pyvdisk.vscript.mounts
    from_api: "rpc:pyvdisk.vscript.cli._mounts"
    to_api: "rpc:pyvdisk.vscript.mounts.MountRegistry#grant"
    label: {zh: "授予挂载", en: "grants mounts"}
---
