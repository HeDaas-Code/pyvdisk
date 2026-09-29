---
uid: a0000502
id: pyvdisk.storage.vfs.create
parent: pyvdisk.storage.vfs
name: {zh: "创建盘与卷", en: "Create Disk or Volume"}
description:
  zh: >
      VFS 门面上的磁盘与卷创建入口。
      
  en: >
      Disk and volume creation entry points on the VFS facade.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 101
    end_line: 142
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#create"
    description:
      zh: >
          格式化新的单盘文件系统镜像。
          
      en: >
          Format a new single-disk filesystem image.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#create_volume"
    description:
      zh: >
          创建多盘卷并格式化。
          
      en: >
          Create a multi-disk volume and format it.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.mkfs
    from_api: "rpc:pyvdisk.vfs.VFS#create"
    label: {zh: "格式化磁盘", en: "formats disk"}
---
