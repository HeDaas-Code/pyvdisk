---
uid: a0000417
id: pyvdisk.storage.fs.mkfs
parent: pyvdisk.storage.fs
name: {zh: "格式化", en: "Format"}
description:
  zh: >
      格式化：构建带保留区的空文件系统，并写入磁盘身份尾标；身份写入不可用时不影响格式化。
      
  en: >
      Formatting: builds an empty filesystem with reserved regions and stamps the disk identity trailer without failing the format when identity writing is unavailable.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 1229
    end_line: 1330
apis:
  - protocol: rpc
    path: "pyvdisk.fs.mkfs"
    description:
      zh: >
          格式化镜像：写入超级块、位图、根目录与磁盘身份尾标。
          
      en: >
          Format a disk image: write the superblock, bitmaps, root directory and the disk identity trailer.
          
deps:
  - kind: call
    to: pyvdisk.storage.identity.probe
    from_api: "rpc:pyvdisk.fs.mkfs"
    to_api: "rpc:pyvdisk.identity.write_identity_to_block0"
    label: {zh: "写入身份尾标", en: "stamps identity"}
---
