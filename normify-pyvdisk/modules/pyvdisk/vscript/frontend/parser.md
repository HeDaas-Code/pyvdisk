---
uid: a0000a04
id: pyvdisk.vscript.frontend.parser
parent: pyvdisk.vscript.frontend
name: {zh: "语法解析器", en: "Parser"}
description:
  zh: >
      语法实现：语句、声明、控制流、match 分支与工作流构造。
      
  en: >
      Grammar implementation: statements, declarations, control flow, match arms and the workflow constructs.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 71f29c6ad29ae5453ef68af56bc96aa54ae9d0f95c23e0c633f8bf4d231ac79e
source:
  - path: "pyvdisk/vscript/parser.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.parser.Parser"
    description:
      zh: >
          递归下降语句解析器，表达式部分用 Pratt 解析。
          
      en: >
          Recursive-descent statement parser with Pratt expression parsing.
          
  - protocol: rpc
    path: "pyvdisk.vscript.parser.parse"
    description:
      zh: >
          对源字符串做词法与语法分析并返回 Program 的便利函数。
          
      en: >
          Convenience function lexing and parsing a source string into a Program.
          
deps:
  - kind: call
    to: pyvdisk.vscript.frontend.lexer
    from_api: "rpc:pyvdisk.vscript.parser.parse"
    to_api: "rpc:pyvdisk.vscript.lexer.lex"
    label: {zh: "词法分析", en: "lexes source"}
  - kind: dataflow
    to: pyvdisk.vscript.frontend.ast
    from_api: "rpc:pyvdisk.vscript.parser.Parser"
    to_api: "rpc:pyvdisk.vscript.ast.Program"
    label: {zh: "构建 AST", en: "builds AST"}
---
