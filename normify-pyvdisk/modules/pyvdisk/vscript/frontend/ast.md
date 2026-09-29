---
uid: a0000a03
id: pyvdisk.vscript.frontend.ast
parent: pyvdisk.vscript.frontend
name: {zh: "AST 节点", en: "AST Nodes"}
description:
  zh: >
      AST 节点词表：表达式、语句、声明，以及工作流特有的 transaction、task、parallel 与 await 节点。
      
  en: >
      The AST node vocabulary: expressions, statements, declarations and the workflow-specific transaction, task, parallel and await nodes.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 169e17c9bfb255011f2591c4a267a9db6425c10791bb0202e196977753ef435d
source:
  - path: "pyvdisk/vscript/ast.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.ast.Node"
    description:
      zh: >
          携带源码位置的 AST 节点基类。
          
      en: >
          Base AST node carrying its source span.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.Program"
    description:
      zh: >
          持有语句列表与语言版本的根节点。
          
      en: >
          Root node holding the statement list and language version.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.Let"
    description:
      zh: >
          let / 常量声明，可选 export。
          
      en: >
          Let or constant declaration, optionally exported.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.If"
    description:
      zh: >
          条件语句，含可选 else 分支。
          
      en: >
          Conditional statement with optional else branch.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.FunctionDecl"
    description:
      zh: >
          带块体的具名函数声明。
          
      en: >
          Named function declaration with a block body.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.Import"
    description:
      zh: >
          带可选别名的模块导入。
          
      en: >
          Module import with an optional alias.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.Requirement"
    description:
      zh: >
          声明能力及其权限的 require 节点。
          
      en: >
          Requirement declaration naming a capability and its permissions.
          
  - protocol: rpc
    path: "pyvdisk.vscript.ast.Transaction"
    description:
      zh: >
          事务块节点。
          
      en: >
          Transaction block node.
          
deps:
  - kind: reference
    to: pyvdisk.vscript.frontend.span
    to_api: "rpc:pyvdisk.vscript.errors.SourceSpan"
    label: {zh: "位置来自 errors 模块", en: "spans from errors module"}
---
