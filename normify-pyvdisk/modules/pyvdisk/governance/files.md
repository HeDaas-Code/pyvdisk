---
uid: a000080f
id: pyvdisk.governance.files
parent: pyvdisk.governance
name: {zh: "受限文件系统", en: "Scoped Filesystem"}
description:
  zh: >
      能力治理的文件系统半边：每个 VFS 方法都必须经过权限与范围检查才能触达。
      
  en: >
      Filesystem half of capability governance: every VFS method is reachable only through a permission and scope check.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 799d79402415a8648a6a253e7d9d33664cfd27b7cb5f751693abb7efd6c3cb64
source:
  - path: "pyvdisk/infrastructure/capabilities.py"
    line: 50
    end_line: 81
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace"
    description:
      zh: >
          在每次文件系统调用前检查逐路径权限的 VFS 适配器。
          
      en: >
          VFS adapter that checks a per-path permission before every filesystem call.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#_check_file"
    description:
      zh: >
          检查单个路径的读、写或删除权限。
          
      en: >
          Check read, write or delete permission on one path.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#exists"
    description:
      zh: >
          带权限检查的路径存在性判定。
          
      en: >
          Permission-checked path existence test.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#listdir"
    description:
      zh: >
          带权限检查的目录列举。
          
      en: >
          Permission-checked directory listing.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#read_file"
    description:
      zh: >
          带权限检查的整文件读取。
          
      en: >
          Permission-checked whole-file read.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#write_file"
    description:
      zh: >
          带权限检查的整文件写入。
          
      en: >
          Permission-checked whole-file write.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#rmtree"
    description:
      zh: >
          带权限检查的递归删除。
          
      en: >
          Permission-checked recursive removal.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.capabilities.ScopedFileNamespace#fsck"
    description:
      zh: >
          运行 fsck，修复时要求 admin 能力。
          
      en: >
          Run fsck, requiring the admin capability when repairing.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.files
    from_api: "rpc:pyvdisk.infrastructure.capabilities.ScopedFileNamespace#read_file"
    to_api: "rpc:pyvdisk.vfs.VFS#read_file"
    label: {zh: "委托给 VFS", en: "delegates to VFS"}
---
