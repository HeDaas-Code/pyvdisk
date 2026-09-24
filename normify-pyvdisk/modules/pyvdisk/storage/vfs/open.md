---
uid: a0000501
id: pyvdisk.storage.vfs.open
parent: pyvdisk.storage.vfs
name: {zh: "VFS 打开", en: "VFS Open"}
description:
  zh: >
      VFS 构造与传输选择：单个镜像可按普通盘或多成员卷打开。
      
  en: >
      VFS construction and transport selection: one image is opened either as a plain disk or as a multi-member volume.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 24
    end_line: 100
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS"
    description:
      zh: >
          单个磁盘或卷之上的高层路径视图。
          
      en: >
          High-level path-based view over one disk or volume.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#__init__"
    description:
      zh: >
          把 VFS 绑定到路径；底层盘在 mount 时打开。
          
      en: >
          Bind a VFS to a path; the underlying disk is opened during mount.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#_open_disk_or_volume"
    description:
      zh: >
          打开盘文件，自动识别是单盘还是卷。
          
      en: >
          Open a disk file, auto-detecting whether it is a single disk or a volume.
          
deps:
  - kind: call
    to: pyvdisk.storage.block.image
    from_api: "rpc:pyvdisk.vfs.VFS#_open_disk_or_volume"
    to_api: "rpc:pyvdisk.disk.VirtualDisk#open"
    label: {zh: "打开镜像", en: "opens image"}
---
