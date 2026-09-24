---
uid: a0000b03
id: pyvdisk.vscript.runtime.callables
parent: pyvdisk.vscript.runtime
name: {zh: "可调用对象与任务", en: "Callables and Tasks"}
description:
  zh: >
      可调用对象与任务：参数绑定、对定义作用域的闭包，以及 await 等待的任务句柄。
      
  en: >
      Callables and tasks: parameter binding, closures over the defining scope and the task handle awaited by await.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.261Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 140
    end_line: 176
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Task"
    description:
      zh: >
          parallel 构造产出的确定性任务句柄。
          
      en: >
          Deterministic task handle produced by the parallel construct.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Task#await_result"
    description:
      zh: >
          返回任务结果，并重新抛出其错误。
          
      en: >
          Return the task result, re-raising its error.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Function"
    description:
      zh: >
          已声明函数的可调用包装，负责参数绑定。
          
      en: >
          Callable wrapper around a declared function, binding parameters.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Function#__call__"
    description:
      zh: >
          以新的子作用域调用函数。
          
      en: >
          Invoke the function with a fresh child scope.
          
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.LambdaFunction"
    description:
      zh: >
          表达式体的 lambda 可调用对象。
          
      en: >
          Expression-bodied lambda callable.
          
---
