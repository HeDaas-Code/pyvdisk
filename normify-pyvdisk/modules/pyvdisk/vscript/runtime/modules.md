---
uid: a0000b06
id: pyvdisk.vscript.runtime.modules
parent: pyvdisk.vscript.runtime
name: {zh: "模块加载", en: "Module Loading"}
description:
  zh: >
      模块加载：在内置原生模块与已配置模块根下解析 import 名称。
      
  en: >
      Module loading: resolves import names against built-in native modules and configured module roots.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.263Z"
fingerprint: 2ddb2e01919be6c65aac4dd5d0babfa3f19bb115f24b6fa6da68c57b3b4756ef
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 304
    end_line: 322
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.runtime.Runtime#load_module"
    description:
      zh: >
          在已配置的模块根下解析并执行 import。
          
      en: >
          Resolve and execute an import against the configured module roots.
          
deps:
  - kind: call
    to: pyvdisk.vscript.stdlib.factory
    from_api: "rpc:pyvdisk.vscript.runtime.Runtime#load_module"
    to_api: "rpc:pyvdisk.vscript.stdlib.create_stdlib"
    label: {zh: "加载原生模块", en: "loads native module"}
---
