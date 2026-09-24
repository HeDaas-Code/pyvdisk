---
uid: a0000b08
id: pyvdisk.vscript.stdlib.native
parent: pyvdisk.vscript.stdlib
name: {zh: "原生模块", en: "Native Modules"}
description:
  zh: >
      原生模块基础设施与 Handle 包装：让原生资源留在能力检查之后，而非暴露裸 Python 对象。
      
  en: >
      Native module plumbing and the Handle wrapper that keeps native resources behind capability checks rather than raw Python objects.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.265Z"
fingerprint: c8f6852ff21b7b08e89e6c158274eeaef3d0a02376ac5600831b15124942de6e
source:
  - path: "pyvdisk/vscript/stdlib.py"
    line: 9
    end_line: 26
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.NativeFunction"
    description:
      zh: >
          暴露给脚本的原生函数包装。
          
      en: >
          Native function wrapper exposed to scripts.
          
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.NativeModule"
    description:
      zh: >
          组成单个可导入模块的具名原生成员集合。
          
      en: >
          Named collection of native members forming one importable module.
          
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.NativeModule#member"
    description:
      zh: >
          解析原生模块的成员。
          
      en: >
          Resolve a member of the native module.
          
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.Handle"
    description:
      zh: >
          对已授予能力的不透明脚本可见包装。
          
      en: >
          Opaque script-visible wrapper around a granted capability.
          
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.Handle#kind"
    description:
      zh: >
          报告句柄所指资源的类型。
          
      en: >
          Report the kind of resource the handle refers to.
          
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib.Handle#name"
    description:
      zh: >
          报告脚本可见的句柄名称。
          
      en: >
          Report the handle name visible to the script.
          
deps:
  - kind: reference
    to: pyvdisk.vscript.policy.capability
    from_api: "rpc:pyvdisk.vscript.stdlib.Handle"
    to_api: "rpc:pyvdisk.vscript.policy.Capability"
    label: {zh: "包装能力", en: "wraps capability"}
---
