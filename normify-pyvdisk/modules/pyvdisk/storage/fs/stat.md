---
uid: a0000406
id: pyvdisk.storage.fs.stat
parent: pyvdisk.storage.fs
name: {zh: "Stat 视图", en: "Stat View"}
description:
  zh: >
      stat 结果对象及类型判定，供 VFS、FUSE 与 CLI 使用。
  en: >
      Stat result object with the type predicates consumed by VFS, FUSE and the CLI.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 229
    end_line: 251
apis:
  - protocol: rpc
    path: "pyvdisk.fs.Stat"
    description:
      zh: >
          返回给调用方的只读 stat 视图。
      en: >
          Read-only stat view returned to callers.
  - protocol: rpc
    path: "pyvdisk.fs.Stat#is_dir"
    description:
      zh: >
          inode 是目录（或指向目录的符号链接）时为真。
      en: >
          True when the inode is a directory or symlink pointing at one.
  - protocol: rpc
    path: "pyvdisk.fs.Stat#is_file"
    description:
      zh: >
          inode 是普通文件时为真。
      en: >
          True when the inode is a regular file.
  - protocol: rpc
    path: "pyvdisk.fs.Stat#is_symlink"
    description:
      zh: >
          inode 是符号链接时为真。
      en: >
          True when the inode is a symbolic link.
---
