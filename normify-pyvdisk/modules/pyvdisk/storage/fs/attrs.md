---
uid: a000040f
id: pyvdisk.storage.fs.attrs
parent: pyvdisk.storage.fs
name: {zh: "属性与链接", en: "Attributes and Links"}
description:
  zh: >
      属性与链接：硬链接、模式、属主、时间戳，以及 VFS 使用的权限检查。
  en: >
      Attributes and links: hard links, mode, ownership, timestamps and the permission check used by VFS.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 643
    end_line: 701
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#link"
    description:
      zh: >
          从既有路径创建指向新名字的硬链接。
      en: >
          Create a hard link from an existing path to a new name.
  - protocol: rpc
    path: "pyvdisk.fs.FS#chmod"
    description:
      zh: >
          修改 inode 权限位。
      en: >
          Change inode permission bits.
  - protocol: rpc
    path: "pyvdisk.fs.FS#chown"
    description:
      zh: >
          修改 inode 属主与属组。
      en: >
          Change inode owner and group.
  - protocol: rpc
    path: "pyvdisk.fs.FS#utime"
    description:
      zh: >
          设置 inode 访问与修改时间。
      en: >
          Set inode access and modification times.
  - protocol: rpc
    path: "pyvdisk.fs.FS#access"
    description:
      zh: >
          针对 uid/gid 的 POSIX 模式位访问检查。
      en: >
          POSIX mode-bit access check for a uid/gid pair.
---
