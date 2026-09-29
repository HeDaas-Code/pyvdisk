---
uid: a0000410
id: pyvdisk.storage.fs.create
parent: pyvdisk.storage.fs
name: {zh: "创建节点", en: "Node Creation"}
description:
  zh: >
      节点创建：文件、目录、符号链接及其共享构造器。
      
  en: >
      Node creation: files, directories, symlinks and their shared constructor.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 703
    end_line: 778
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#_create_node"
    description:
      zh: >
          文件、目录与符号链接共享的节点构造器。
          
      en: >
          Shared node constructor for files, directories and symlinks.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#create"
    description:
      zh: >
          在指定路径创建普通文件。
          
      en: >
          Create a regular file at a path.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#mkdir"
    description:
      zh: >
          在指定路径创建目录。
          
      en: >
          Create a directory at a path.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#symlink"
    description:
      zh: >
          创建指向目标字符串的符号链接。
          
      en: >
          Create a symbolic link pointing at a target string.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#readlink"
    description:
      zh: >
          读取符号链接 inode 的目标。
          
      en: >
          Read the target of a symlink inode.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.inode-io
    from_api: "rpc:pyvdisk.fs.FS#_create_node"
    to_api: "rpc:pyvdisk.fs.FS#alloc_inode"
    label: {zh: "分配 inode", en: "reserves inode"}
---
