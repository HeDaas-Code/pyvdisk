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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.262Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 323
    end_line: 389
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
