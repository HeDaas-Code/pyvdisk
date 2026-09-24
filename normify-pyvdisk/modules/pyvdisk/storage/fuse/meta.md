---
uid: a000070e
id: pyvdisk.storage.fuse.meta
parent: pyvdisk.storage.fuse
name: {zh: "FUSE 属性", en: "FUSE Attributes"}
description:
  zh: >
      FUSE 可用性检测，以及操作表中属性与目录列举部分。
      
  en: >
      FUSE availability check and the attribute/listing half of the operation table.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 5fe2c5a2cde43ccd63a7a2c90ca4f237f91e4c1de74900e83ebc49d9e6dc5193
source:
  - path: "pyvdisk/fuse_mount.py"
    line: 24
    end_line: 80
apis:
  - protocol: rpc
    path: "pyvdisk.fuse_mount._have_fuse"
    description:
      zh: >
          fusepy 可导入时为真。
          
      en: >
          True when fusepy is importable.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations"
    description:
      zh: >
          把内核调用翻译为 VFS 调用的 FUSE 操作类。
          
      en: >
          FUSE operation class translating kernel calls into VFS calls.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_getattr"
    description:
      zh: >
          通过 VFS stat 实现 getattr。
          
      en: >
          Implement getattr by statting through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_readdir"
    description:
      zh: >
          通过列举 VFS 目录实现 readdir。
          
      en: >
          Implement readdir by listing the VFS directory.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.stat
    from_api: "rpc:pyvdisk.fuse_mount._VFuseOperations#_getattr"
    to_api: "rpc:pyvdisk.vfs.VFS#stat"
    label: {zh: "取 stat", en: "stats path"}
---
