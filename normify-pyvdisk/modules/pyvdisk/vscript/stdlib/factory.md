---
uid: a0000b0a
id: pyvdisk.vscript.stdlib.factory
parent: pyvdisk.vscript.stdlib
name: {zh: "标准库工厂", en: "Stdlib Factory"}
description:
  zh: >
      标准库工厂：文件系统、向量、日志与 json 原生函数，均受能力守卫与字节预算约束。每个会改动的 fs 动词在触碰存储之前先记入撤销账，事务失败时可回滚，而不留半成品写入。
      
  en: >
      Stdlib factory: filesystem, vector, log and json native functions, all behind capability guards and byte budgets. Every mutating fs verb journals its undo record before it touches the store, so a failed transaction can be rolled back instead of leaving half-applied writes.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.264Z"
fingerprint: c8f6852ff21b7b08e89e6c158274eeaef3d0a02376ac5600831b15124942de6e
source:
  - path: "pyvdisk/vscript/stdlib.py"
    line: 46
    end_line: 118
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.create_stdlib"
    description:
      zh: >
          构建绑定到单个运行时的 fs、vector、log 与 json 原生模块。
          
      en: >
          Build the fs, vector, log and json native modules bound to one runtime.
          
deps:
  - kind: call
    to: pyvdisk.vscript.stdlib.guards
    from_api: "rpc:pyvdisk.vscript.stdlib.create_stdlib"
    to_api: "rpc:pyvdisk.vscript.stdlib._cap"
    label: {zh: "使用守卫", en: "uses guards"}
  - kind: call
    to: pyvdisk.vscript.stdlib.native
    from_api: "rpc:pyvdisk.vscript.stdlib.create_stdlib"
    to_api: "rpc:pyvdisk.vscript.stdlib.NativeModule"
    label: {zh: "包装原生模块", en: "wraps native modules"}
---
