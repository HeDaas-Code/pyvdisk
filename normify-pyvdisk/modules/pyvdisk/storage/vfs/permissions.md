---
uid: a0000504
id: pyvdisk.storage.vfs.permissions
parent: pyvdisk.storage.vfs
name: {zh: "权限门禁", en: "Permission Gate"}
description:
  zh: >
      每次 VFS 变更前的权限门禁：inode 模式位、路径遍历与父目录检查。
      
  en: >
      The permission gate applied before every VFS mutation: inode bits, path traversal and parent-directory checks.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 163
    end_line: 202
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#_fs_or_raise"
    description:
      zh: >
          返回已挂载的 FS，未挂载时抛错。
          
      en: >
          Return the mounted FS or raise when the VFS was never mounted.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#_perm_enabled"
    description:
      zh: >
          除显式关闭权限检查外为真。
          
      en: >
          True unless permission checks are explicitly disabled.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#_check"
    description:
      zh: >
          inode 不满足请求位时抛出 PermissionError。
          
      en: >
          Raise PermissionError unless the inode grants the requested bits.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#_check_traverse"
    description:
      zh: >
          要求路径上每一级目录具备执行权限。
          
      en: >
          Require execute permission on every directory along a path.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#_check_parent"
    description:
      zh: >
          要求路径父目录具备指定权限。
          
      en: >
          Require permission on the parent directory of a path.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.attrs
    from_api: "rpc:pyvdisk.vfs.VFS#_check"
    to_api: "rpc:pyvdisk.fs.FS#access"
    label: {zh: "POSIX 权限检查", en: "POSIX access check"}
---
