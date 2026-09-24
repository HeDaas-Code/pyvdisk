---
uid: a0000b0c
id: pyvdisk.vscript.host.module
parent: pyvdisk.vscript.host
name: {zh: "宿主模块", en: "Host Module"}
description:
  zh: >
      host 原生模块：面向脚本的读取、写入与传输入口，全部经隔离代理。
      
  en: >
      The host native module: script-facing read, write and transfer entry points that all funnel through the confinement proxy.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.026Z"
fingerprint: 4bfbe1157d25b89c581f1b0dd4d4eb9d42fbe2c4b817c4371782f6bc007e4742
source:
  - path: "pyvdisk/vscript/host.py"
    line: 80
    end_line: 92
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.host.create_host_module"
    description:
      zh: >
          构建含 read、write、import_file 与 export_file 的 host 原生模块。
          
      en: >
          Build the host native module with read, write, import_file and export_file.
          
deps:
  - kind: call
    to: pyvdisk.vscript.host.guard
    from_api: "rpc:pyvdisk.vscript.host.create_host_module"
    to_api: "rpc:pyvdisk.vscript.host.HostProxy#read"
    label: {zh: "经代理限权", en: "guards via proxy"}
---
