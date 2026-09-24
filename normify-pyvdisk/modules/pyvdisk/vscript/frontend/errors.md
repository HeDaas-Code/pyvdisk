---
uid: a0000a06
id: pyvdisk.vscript.frontend.errors
parent: pyvdisk.vscript.frontend
name: {zh: "错误类型", en: "Error Types"}
description:
  zh: >
      错误层次：把语言各阶段映射为可区分、可捕获、可审计的失败。
      
  en: >
      The error hierarchy that maps language phases to distinguishable, catchable and auditable failures.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: b30ccf2593d5b73a8f9b6644f111e23bb1a7ca5878893f4efa8ce4bbca7ebc2c
source:
  - path: "pyvdisk/vscript/errors.py"
    line: 52
    end_line: 133
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.errors.VScriptError"
    description:
      zh: >
          所有 VScript 失败的基类错误，携带诊断与位置。
          
      en: >
          Base error carrying a diagnostic and span for every VScript failure.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.LexError"
    description:
      zh: >
          扫描器抛出的词法失败。
          
      en: >
          Lexical failure raised by the scanner.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.ParseError"
    description:
      zh: >
          解析器抛出的语法失败。
          
      en: >
          Syntactic failure raised by the parser.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.CompileError"
    description:
      zh: >
          执行前准备阶段抛出的失败。
          
      en: >
          Failure raised while preparing a program for execution.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.RuntimeError"
    description:
      zh: >
          脚本执行过程中的运行时失败。
          
      en: >
          Runtime failure inside an executing script.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.CapabilityError"
    description:
      zh: >
          脚本触及授权外资源时抛出。
          
      en: >
          Raised when a script touches a resource outside its granted capabilities.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.ResourceLimitError"
    description:
      zh: >
          步骤、字节等策略预算耗尽时抛出。
          
      en: >
          Raised when a policy budget such as steps or bytes is exhausted.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.ScriptThrown"
    description:
      zh: >
          封装脚本自身 throw 的值。
          
      en: >
          Wraps a value thrown by the script itself.
          
deps:
  - kind: reference
    to: pyvdisk.vscript.frontend.span
    to_api: "rpc:pyvdisk.vscript.errors.Diagnostic"
    label: {zh: "由诊断构造", en: "built from diagnostics"}
---
