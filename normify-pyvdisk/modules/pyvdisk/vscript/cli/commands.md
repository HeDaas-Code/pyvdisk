---
uid: a0000c01
id: pyvdisk.vscript.cli.commands
parent: pyvdisk.vscript.cli
name: {zh: "VScript 命令", en: "VScript Commands"}
description:
  zh: >
      VScript 命令接口：参数解析、挂载授权与 check/run 入口，含使 host.* 可用的宿主读/写根目录选项。
      
  en: >
      VScript command surface: argument parsing, mount authorisation and the check/run entry points, including the host read/write root options that make host.* usable.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.259Z"
fingerprint: b93664d4ede6142b0a1f77adbe3592f0ee285c15f7e00e3627f7acae3a5a3431
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
