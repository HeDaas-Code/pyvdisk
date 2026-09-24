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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 1dda7ccf92f423de4bf6c96608977fd7dd9663e017104e9b8dd34066202d0dad
source:
  - path: "pyvdisk/vscript/runtime.py"
    line: 222
    end_line: 240
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
