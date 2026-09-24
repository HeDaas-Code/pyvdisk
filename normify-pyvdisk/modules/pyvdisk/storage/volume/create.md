---
uid: a0000707
id: pyvdisk.storage.volume.create
parent: pyvdisk.storage.volume
name: {zh: "卷创建", en: "Volume Creation"}
description:
  zh: >
      VFS 门面与 CLI 使用的卷创建与打开辅助。
      
  en: >
      Volume creation and opening helpers used by the VFS facade and the CLI.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 479
    end_line: 557
apis:
  - protocol: rpc
    path: "pyvdisk.volume.create_volume"
    description:
      zh: >
          创建成员、写入卷描述符并在卷上格式化文件系统。
          
      en: >
          Create members, write the volume descriptor and format a filesystem over the volume.
          
  - protocol: rpc
    path: "pyvdisk.volume.open_volume"
    description:
      zh: >
          从成员路径打开既有卷。
          
      en: >
          Open an existing volume from its member paths.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.mkfs
    from_api: "rpc:pyvdisk.volume.create_volume"
    label: {zh: "格式化卷", en: "formats volume"}
---
