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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 139
    end_line: 221
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
