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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 57
    end_line: 93
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
