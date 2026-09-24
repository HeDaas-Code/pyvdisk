---
uid: a0000a01
id: pyvdisk.vscript.frontend.tokens
parent: pyvdisk.vscript.frontend
name: {zh: "词法单元", en: "Token Types"}
description:
  zh: >
      语言的词法单元词表：lexer 能产出的全部关键字、运算符与字面量。
      
  en: >
      The token vocabulary of the language: every keyword, operator and literal the lexer can emit.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.310Z"
fingerprint: ba8c01c0d894a1eea1877104b4f729f40f057a27f38fcf137157f2d5e9e7b00d
source:
  - path: "pyvdisk/vscript/tokens.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.tokens.TokenType"
    description:
      zh: >
          词法单元类型枚举：关键字、运算符、字面量与结构符号。
          
      en: >
          Token kind enum covering keywords, operators, literals and structural tokens.
          
  - protocol: rpc
    path: "pyvdisk.vscript.tokens.Token"
    description:
      zh: >
          一个已词法化的单元，携带类型、字面、位置与可选值。
          
      en: >
          A lexed token carrying type, lexeme, span and optional value.
          
  - protocol: rpc
    path: "pyvdisk.vscript.tokens.Token#is_eof"
    description:
      zh: >
          该单元为输入终止符时为真。
          
      en: >
          True when the token terminates input.
          
deps:
  - kind: reference
    to: pyvdisk.vscript.frontend.span
    to_api: "rpc:pyvdisk.vscript.errors.SourceSpan"
    label: {zh: "携带源码位置", en: "carries source spans"}
---
