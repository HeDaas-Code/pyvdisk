---
uid: a0000b0b
id: pyvdisk.vscript.host.guard
parent: pyvdisk.vscript.host
name: {zh: "宿主隔离", en: "Host Confinement"}
description:
  zh: >
      宿主隔离：声明脚本可读写的宿主目录，其余路径一律拒绝。写入末尾会刷盘目录，让改名本身落地；该刷盘经由平台适配层，因为 Windows 无法把目录当文件打开。
  en: >
      Host confinement: declares which host directories a script may read and write and refuses everything else. Writes end with a directory flush so the rename itself is durable; that flush goes through the platform layer, since Windows cannot open a directory as a file.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: b041b5a92b2d5d9ff7cfc03f3d5bd925f17d1a1137ec559745e0608f984f0d8a
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
          
deps:
  - kind: call
    to: pyvdisk.platform.durability
    from_api: "rpc:pyvdisk.vscript.host.HostProxy#write"
    label: {zh: "刷盘目录", en: "flush the directory"}
---
