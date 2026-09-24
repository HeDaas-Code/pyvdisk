---
uid: a0000b0a
id: pyvdisk.vscript.stdlib.factory
parent: pyvdisk.vscript.stdlib
name: {zh: "标准库工厂", en: "Stdlib Factory"}
description:
  zh: >
      标准库工厂：文件系统、向量、日志与 json 原生函数，均受能力守卫与字节预算约束。
      
  en: >
      The standard library factory: filesystem, vector, log and json natives, each confined by capability guards and byte budgets.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 4a46271b1688a7dd1e764a4281feb9875dc7c8f8b117cab916ca481882cc7e91
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
