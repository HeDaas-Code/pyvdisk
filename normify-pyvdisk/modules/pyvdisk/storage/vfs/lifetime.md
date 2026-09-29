---
uid: a0000503
id: pyvdisk.storage.vfs.lifetime
parent: pyvdisk.storage.vfs
name: {zh: "挂载生命周期", en: "Mount Lifecycle"}
description:
  zh: >
      挂载与关闭生命周期，包含测试与 CLI 广泛使用的 with 协议。
      
  en: >
      Mount and close lifecycle, including the with-statement protocol used throughout the tests and CLI.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 143
    end_line: 161
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#mount"
    description:
      zh: >
          挂载文件系统并返回自身以链式调用。
          
      en: >
          Mount the filesystem and return self for chaining.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#close"
    description:
      zh: >
          刷新并关闭底层磁盘。
          
      en: >
          Flush and close the underlying disk.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#__enter__"
    description:
      zh: >
          上下文管理器入口，返回已挂载的 VFS。
          
      en: >
          Context manager entry returning a mounted VFS.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#__exit__"
    description:
      zh: >
          上下文管理器退出时关闭 VFS。
          
      en: >
          Context manager exit that closes the VFS.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.mount
    from_api: "rpc:pyvdisk.vfs.VFS#mount"
    to_api: "rpc:pyvdisk.fs.FS#mount"
    label: {zh: "挂载文件系统", en: "mounts filesystem"}
---
