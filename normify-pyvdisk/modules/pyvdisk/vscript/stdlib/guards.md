---
uid: a0000b09
id: pyvdisk.vscript.stdlib.guards
parent: pyvdisk.vscript.stdlib
name: {zh: "原生守卫", en: "Native Guards"}
description:
  zh: >
      每个原生函数触及资源前调用的两个守卫：类型与权限检查，以及路径范围限定。
      
  en: >
      The two guard helpers every native function calls before touching a resource: kind and permission checks, and path scoping.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.265Z"
fingerprint: c8f6852ff21b7b08e89e6c158274eeaef3d0a02376ac5600831b15124942de6e
source:
  - path: "pyvdisk/vscript/stdlib.py"
    line: 28
    end_line: 44
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib._cap"
    description:
      zh: >
          要求句柄为预期类型并持有指定权限。
          
      en: >
          Require a handle to be of an expected kind and to hold the given permissions.
          
  - protocol: rpc
    path: "pyvdisk.vscript.stdlib._vpath"
    description:
      zh: >
          在能力根内归一化并限定脚本路径。
          
      en: >
          Normalize and scope a script path inside a capability root.
          
---
