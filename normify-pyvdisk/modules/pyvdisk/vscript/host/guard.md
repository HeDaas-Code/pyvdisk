---
uid: a0000b0b
id: pyvdisk.vscript.host.guard
parent: pyvdisk.vscript.host
name: {zh: "宿主隔离", en: "Host Confinement"}
description:
  zh: >
      宿主隔离：声明脚本可读写的宿主目录，并拒绝其余一切路径。
  en: >
      Host confinement: declare which host directories a script may read and write, and reject everything else.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 4bfbe1157d25b89c581f1b0dd4d4eb9d42fbe2c4b817c4371782f6bc007e4742
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
