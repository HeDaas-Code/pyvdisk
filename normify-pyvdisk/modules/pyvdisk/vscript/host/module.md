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
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: b041b5a92b2d5d9ff7cfc03f3d5bd925f17d1a1137ec559745e0608f984f0d8a
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
