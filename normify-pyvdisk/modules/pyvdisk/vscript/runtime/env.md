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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.262Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 117
    end_line: 139
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
