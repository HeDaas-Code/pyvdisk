---
uid: a0000b0b
id: pyvdisk.vscript.host.guard
parent: pyvdisk.vscript.host
name: {zh: "宿主隔离", en: "Host Confinement"}
description:
  zh: >
      宿主隔离：声明脚本可读写的宿主目录，其余路径一律拒绝。该策略现在有真实入口——CLI 注入声明的根目录——host.* 不再因根目录为空而不可用。
      
  en: >
      Host confinement: declares which host directories a script may read and write and refuses everything else. The policy now has a real entry point -- the CLI injects the declared roots -- so host.* is reachable instead of failing with an empty root set.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.260Z"
fingerprint: baf58ee2c4dbda56cd6c7afb131bba217cd12b97019cd89fbebb5a1a7edad7c2
source:
  - path: "pyvdisk/vscript/host.py"
    line: 8
    end_line: 79
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.host.HostCapability"
    description:
      zh: >
          宿主模块允许触及的读根与写根。
          
      en: >
          Read and write roots the host module may touch.
          
  - protocol: rpc
    path: "pyvdisk.vscript.host.HostCapability#proxy"
    description:
      zh: >
          为该能力构建脚本可见的宿主代理。
          
      en: >
          Build the script-visible host proxy for this capability.
          
  - protocol: rpc
    path: "pyvdisk.vscript.host.HostProxy"
    description:
      zh: >
          强制执行读/写根白名单的宿主文件系统代理。
          
      en: >
          Allowlisted host filesystem proxy enforcing read and write roots.
          
  - protocol: rpc
    path: "pyvdisk.vscript.host.HostProxy#_check"
    description:
      zh: >
          拒绝声明根之外的路径。
          
      en: >
          Reject paths outside the declared roots.
          
  - protocol: rpc
    path: "pyvdisk.vscript.host.HostProxy#read"
    description:
      zh: >
          把宿主文件读入内存。
          
      en: >
          Read a host file into memory.
          
  - protocol: rpc
    path: "pyvdisk.vscript.host.HostProxy#write"
    description:
      zh: >
          写入宿主数据，可选禁止覆盖。
          
      en: >
          Write host data with an optional no-overwrite guard.
          
---
