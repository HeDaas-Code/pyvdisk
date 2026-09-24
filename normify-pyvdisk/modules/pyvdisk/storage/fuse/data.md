---
uid: a000070f
id: pyvdisk.storage.fuse.data
parent: pyvdisk.storage.fuse
name: {zh: "FUSE 数据处理", en: "FUSE Data Ops"}
description:
  zh: >
      FUSE 数据与命名空间变更：read、write、create、mkdir、rmdir、unlink 与 rename 处理。
      
  en: >
      FUSE data and namespace mutations: read, write, create, mkdir, rmdir, unlink and rename handlers.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.232Z"
fingerprint: b4475de0aa022f77959dd296d825fe99caca40036a8a86be29dcd1e6d6c0cf47
source:
  - path: "pyvdisk/fuse_mount.py"
    line: 85
    end_line: 121
apis:
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_read"
    description:
      zh: >
          通过 VFS 取字节区间实现 read。
          
      en: >
          Implement read by fetching a byte range through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_write"
    description:
      zh: >
          通过 VFS 存字节实现 write。
          
      en: >
          Implement write by storing bytes through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_create"
    description:
      zh: >
          实现 create，只读挂载时拒绝。
          
      en: >
          Implement create, rejecting it when mounted read-only.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_mkdir"
    description:
      zh: >
          通过 VFS 实现 mkdir。
          
      en: >
          Implement mkdir through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_rmdir"
    description:
      zh: >
          通过 VFS 实现 rmdir。
          
      en: >
          Implement rmdir through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_unlink"
    description:
      zh: >
          通过 VFS 实现 unlink。
          
      en: >
          Implement unlink through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_rename"
    description:
      zh: >
          通过 VFS 实现 rename。
          
      en: >
          Implement rename through the VFS.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.files
    from_api: "rpc:pyvdisk.fuse_mount._VFuseOperations#_write"
    to_api: "rpc:pyvdisk.vfs.VFS#write_file"
    label: {zh: "写文件", en: "writes file"}
---
