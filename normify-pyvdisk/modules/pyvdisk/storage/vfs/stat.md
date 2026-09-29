---
uid: a0000509
id: pyvdisk.storage.vfs.stat
parent: pyvdisk.storage.vfs
name: {zh: "元数据读取", en: "Metadata Reads"}
description:
  zh: >
      暴露给调用方与 FUSE 的元数据读取与链接操作。
      
  en: >
      Metadata reads and link operations exposed to callers and to FUSE.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 339
    end_line: 362
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#stat"
    description:
      zh: >
          按路径取 stat，默认跟踪末尾符号链接。
          
      en: >
          Stat a path, following the final symlink by default.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#lstat"
    description:
      zh: >
          不跟踪末尾符号链接地取 stat。
          
      en: >
          Stat a path without following the final symlink.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#symlink"
    description:
      zh: >
          创建符号链接。
          
      en: >
          Create a symbolic link.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#readlink"
    description:
      zh: >
          读取符号链接目标。
          
      en: >
          Read a symbolic link target.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#link"
    description:
      zh: >
          创建硬链接。
          
      en: >
          Create a hard link.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.query
    from_api: "rpc:pyvdisk.vfs.VFS#stat"
    to_api: "rpc:pyvdisk.fs.FS#stat_path"
    label: {zh: "读取 inode", en: "reads inode"}
---
