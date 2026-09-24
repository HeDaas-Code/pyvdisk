---
uid: a0000606
id: pyvdisk.storage.log.open
parent: pyvdisk.storage.log
name: {zh: "日志盘打开", en: "Log Disk Open"}
description:
  zh: >
      LogDisk 生命周期及日志命名空间下按流的 JSON 辅助。
      
  en: >
      LogDisk lifecycle and the per-stream JSON helpers under the log namespace.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.234Z"
fingerprint: 4b31d03456b1ae4db1ebceef13f447e5093e6459bdea0d2d648139d215bd89a4
source:
  - path: "pyvdisk/log_disk.py"
    line: 38
    end_line: 80
apis:
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk"
    description:
      zh: >
          以分段事件日志形式暴露的 .vdisk 镜像。
          
      en: >
          A .vdisk image exposed as a segmented event log.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#create"
    description:
      zh: >
          格式化新的日志盘镜像。
          
      en: >
          Format a new log disk image.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#mount"
    description:
      zh: >
          挂载日志盘并确保日志命名空间存在。
          
      en: >
          Mount the log disk and ensure the log namespace exists.
          
  - protocol: rpc
    path: "pyvdisk.log_disk.LogDisk#close"
    description:
      zh: >
          关闭底层 VFS。
          
      en: >
          Close the underlying VFS.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.lifetime
    from_api: "rpc:pyvdisk.log_disk.LogDisk#mount"
    to_api: "rpc:pyvdisk.vfs.VFS#mount"
    label: {zh: "挂载 VFS", en: "mounts VFS"}
---
