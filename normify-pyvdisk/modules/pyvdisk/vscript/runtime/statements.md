---
uid: a0000b05
id: pyvdisk.vscript.runtime.statements
parent: pyvdisk.vscript.runtime
name: {zh: "语句执行", en: "Statement Execution"}
description:
  zh: >
      语句执行：解释器中最大的分发表，覆盖语言的全部语句种类。
      
  en: >
      Statement execution: the largest dispatch table of the interpreter, covering every statement kind of the language.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.263Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 224
    end_line: 303
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#execute"
    description:
      zh: >
          分发单个语句节点：声明、控制流、循环、match、transaction、task 与 parallel。
          
      en: >
          Dispatch one statement node: declarations, control flow, loops, match, transaction, task and parallel.
          
deps:
  - kind: call
    to: pyvdisk.vscript.runtime.callables
    from_api: "rpc:pyvdisk.vscript.runtime.Runtime#execute"
    to_api: "rpc:pyvdisk.vscript.runtime.Function#__call__"
    label: {zh: "调用与返回", en: "calls and returns"}
---
