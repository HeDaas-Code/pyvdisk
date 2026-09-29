---
uid: a0000a05
id: pyvdisk.vscript.frontend.span
parent: pyvdisk.vscript.frontend
name: {zh: "位置与诊断", en: "Span and Diagnostic"}
description:
  zh: >
      位置与诊断原语：事情发生在哪里，以及如何向用户报告。
      
  en: >
      Position and diagnostic primitives: where something happened and how it is reported to the user.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: b30ccf2593d5b73a8f9b6644f111e23bb1a7ca5878893f4efa8ce4bbca7ebc2c
source:
  - path: "pyvdisk/vscript/errors.py"
    line: 10
    end_line: 51
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.errors.SourceSpan"
    description:
      zh: >
          脚本内的行列范围，并提供零位置哨兵。
          
      en: >
          Line and column range inside a script, with a zero span sentinel.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.SourceSpan#__str__"
    description:
      zh: >
          把位置渲染为 line:col。
          
      en: >
          Render the span as line:col.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.Diagnostic"
    description:
      zh: >
          带严重级别、代码、消息、位置与源码行的诊断。
          
      en: >
          A diagnostic with severity, code, message, span and source line.
          
  - protocol: rpc
    path: "pyvdisk.vscript.errors.Diagnostic#format"
    description:
      zh: >
          把诊断格式化为单行编译器风格输出。
          
      en: >
          Format the diagnostic as a single compiler-style line.
          
---
