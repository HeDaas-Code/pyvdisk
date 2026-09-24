---
uid: a0000c02
id: pyvdisk.vscript.cli.repl
parent: pyvdisk.vscript.cli
name: {zh: "VScript REPL", en: "VScript REPL"}
description:
  zh: >
      交互式 VScript REPL：行包装、值格式化、帮助，以及跨输入保持状态的循环。
      
  en: >
      The interactive VScript REPL: line wrapping, value formatting, help and the loop that keeps state across inputs.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.260Z"
fingerprint: b93664d4ede6142b0a1f77adbe3592f0ee285c15f7e00e3627f7acae3a5a3431
source:
  - path: "pyvdisk/vscript/cli.py"
    line: 47
    end_line: 151
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.cli._repl_source"
    description:
      zh: >
          把 REPL 输入行包装为脚本源码。
          
      en: >
          Wrap a REPL line as a script source.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cli._repl_type"
    description:
      zh: >
          格式化 REPL 值以便展示。
          
      en: >
          Format a REPL value for display.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cli._repl_help"
    description:
      zh: >
          打印 REPL 帮助文本。
          
      en: >
          Print the REPL help text.
          
  - protocol: rpc
    path: "pyvdisk.vscript.cli.repl"
    description:
      zh: >
          在持久解释器状态上的交互式读取-求值-打印循环。
          
      en: >
          Interactive read-eval-print loop over a persistent interpreter state.
          
deps:
  - kind: call
    to: pyvdisk.vscript.runtime.core
    from_api: "rpc:pyvdisk.vscript.cli.repl"
    to_api: "rpc:pyvdisk.vscript.runtime.Runtime#run"
    label: {zh: "运行源码", en: "runs sources"}
---
