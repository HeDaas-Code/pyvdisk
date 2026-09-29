---
uid: a0000a02
id: pyvdisk.vscript.frontend.lexer
parent: pyvdisk.vscript.frontend
name: {zh: "词法器", en: "Lexer"}
description:
  zh: >
      词法器：注释与空白处理、数字与字符串字面量、运算符与最大匹配。
      
  en: >
      The lexer: comment and whitespace handling, number and string literals, operators and maximal-munch matching.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.310Z"
fingerprint: 54c9f38247be141005b9edbef9b5c4c3b7ee922e1267afaedbf49624d146eaff
source:
  - path: "pyvdisk/vscript/lexer.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.lexer.Lexer"
    description:
      zh: >
          对 VScript 源码的最大匹配扫描器。
          
      en: >
          Maximal-munch scanner over VScript source.
          
  - protocol: rpc
    path: "pyvdisk.vscript.lexer.Lexer#scan"
    description:
      zh: >
          把整份源码扫描为以 EOF 结尾的单元列表。
          
      en: >
          Scan the whole source into a token list ending with EOF.
          
  - protocol: rpc
    path: "pyvdisk.vscript.lexer.Lexer#peek"
    description:
      zh: >
          不消费地向前查看 n 个单元。
          
      en: >
          Look ahead n tokens without consuming.
          
  - protocol: rpc
    path: "pyvdisk.vscript.lexer.Lexer#advance"
    description:
      zh: >
          消费并返回下一个字符。
          
      en: >
          Consume and return the next character.
          
  - protocol: rpc
    path: "pyvdisk.vscript.lexer.lex"
    description:
      zh: >
          对源字符串做词法分析的便利函数。
          
      en: >
          Convenience function lexing a source string.
          
deps:
  - kind: call
    to: pyvdisk.vscript.frontend.errors
    from_api: "rpc:pyvdisk.vscript.lexer.Lexer#scan"
    to_api: "rpc:pyvdisk.vscript.errors.LexError"
    label: {zh: "抛出词法错误", en: "raises lex errors"}
---
