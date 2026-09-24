---
uid: a0000b02
id: pyvdisk.vscript.runtime.env
parent: pyvdisk.vscript.runtime
name: {zh: "作用域与控制流", en: "Scope and Flow"}
description:
  zh: >
      作用域与控制流机制：Env 链，以及以异常实现 return、break、continue 的信号。
  en: >
      Scope and control-flow machinery: the Env chain and the exception-based signals that implement return, break and continue.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 34
    end_line: 54
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Env"
    description:
      zh: >
          带父链与常量名集合的词法作用域。
      en: >
          Lexical scope with a parent chain and a set of constant names.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Env#define"
    description:
      zh: >
          在本层声明名字，可选常量。
      en: >
          Declare a name in this scope, optionally constant.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Env#get"
    description:
      zh: >
          沿作用域链解析名字。
      en: >
          Resolve a name through the scope chain.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Env#set"
    description:
      zh: >
          为已存在名字赋值，拒绝修改常量。
      en: >
          Assign an existing name, rejecting constants.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.ReturnFlow"
    description:
      zh: >
          携带返回值的控制流信号。
      en: >
          Control-flow signal carrying a return value.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.BreakFlow"
    description:
      zh: >
          解开循环的控制流信号。
      en: >
          Control-flow signal unwinding a loop.
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.ContinueFlow"
    description:
      zh: >
          继续循环的控制流信号。
      en: >
          Control-flow signal continuing a loop.
---
