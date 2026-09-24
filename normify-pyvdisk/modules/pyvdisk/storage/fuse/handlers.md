---
uid: a0000710
id: pyvdisk.storage.fuse.handlers
parent: pyvdisk.storage.fuse
name: {zh: "FUSE 链接处理", en: "FUSE Link Ops"}
description:
  zh: >
      其余 FUSE 处理：truncate、链接、open/release、chmod，以及动态 Operations 子类装配。
  en: >
      Remaining FUSE handlers: truncate, links, open/release, chmod and the dynamic Operations subclass assembly.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 5fe2c5a2cde43ccd63a7a2c90ca4f237f91e4c1de74900e83ebc49d9e6dc5193
source:
  - path: "pyvdisk/fuse_mount.py"
    line: 119
    end_line: 233
apis:
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_truncate"
    description:
      zh: >
          通过 VFS 实现 truncate。
      en: >
          Implement truncate through the VFS.
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_symlink"
    description:
      zh: >
          实现符号链接创建。
      en: >
          Implement symlink creation.
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_readlink"
    description:
      zh: >
          实现 readlink。
      en: >
          Implement readlink.
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_open"
    description:
      zh: >
          实现 open，并检查写模式权限。
      en: >
          Implement open with write-mode permission checking.
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_release"
    description:
      zh: >
          实现 release，清理缓存状态。
      en: >
          Implement release by dropping cached state.
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_chmod"
    description:
      zh: >
          实现 chmod，并带只读保护。
      en: >
          Implement chmod with a read-only guard.
  - protocol: rpc
    path: "pyvdisk.fuse_mount._build_fuse_class"
    description:
      zh: >
          根据处理表装配 fusepy 的 Operations 子类。
      en: >
          Assemble the fusepy Operations subclass from the handler table.
---
