---
uid: a000050d
id: pyvdisk.storage.vfs.space
parent: pyvdisk.storage.vfs
name: {zh: "空间与维护", en: "Space and Maintenance"}
description:
  zh: >
      VFS 门面暴露的诊断与维护能力：空间统计、一致性检查与在线扩容。
      
  en: >
      Diagnostics and maintenance exposed by the VFS facade: space accounting, consistency checking and online growth.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 459
    end_line: 499
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#statfs"
    description:
      zh: >
          文件系统几何与剩余空间统计。
          
      en: >
          Filesystem geometry and free-space statistics.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#df"
    description:
      zh: >
          对应 df 的可读空间汇总。
          
      en: >
          Human-readable space summary mirroring df.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#du"
    description:
      zh: >
          子树递归占用字节数。
          
      en: >
          Recursive disk usage of a subtree in bytes.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#fsck"
    description:
      zh: >
          运行文件系统一致性检查。
          
      en: >
          Run a filesystem consistency check.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#grow"
    description:
      zh: >
          就地扩容已挂载文件系统。
          
      en: >
          Grow the mounted filesystem in place.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.walk
    from_api: "rpc:pyvdisk.vfs.VFS#du"
    label: {zh: "遍历目录树", en: "walks tree"}
---
