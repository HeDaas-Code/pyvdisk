---
uid: a0000b07
id: pyvdisk.vscript.runtime.expressions
parent: pyvdisk.vscript.runtime
name: {zh: "表达式求值", en: "Expression Evaluation"}
description:
  zh: >
      表达式求值：字面量、运算符、调用、成员与下标访问，以及赋值语义。
  en: >
      Expression evaluation: literals, operators, calls, member and index access, and assignment semantics.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 241
    end_line: 307
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#eval"
    description:
      zh: >
          求值单个表达式节点，含短路与可选成员语义。
      en: >
          Evaluate one expression node, including short-circuit and optional-member semantics.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#member"
    description:
      zh: >
          解析对象或句柄上的成员访问。
      en: >
          Resolve a member access on an object or handle.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#assign"
    description:
      zh: >
          向名字、下标或成员目标赋值。
      en: >
          Assign to a name, index or member target.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#apply_assign"
    description:
      zh: >
          应用复合或一元赋值运算符。
      en: >
          Apply a compound or unary assignment operator.
---
