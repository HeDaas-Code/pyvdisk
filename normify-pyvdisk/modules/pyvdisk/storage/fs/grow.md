---
uid: a0000416
id: pyvdisk.storage.fs.grow
parent: pyvdisk.storage.fs
name: {zh: "在线扩容", en: "Online Grow"}
description:
  zh: >
      在线扩容：扩大底层镜像并重写超级块几何。
      
  en: >
      Online growth: enlarge the underlying image and rewrite the superblock geometry.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 1197
    end_line: 1226
apis:
  - protocol: rpc
    path: "pyvdisk.fs.grow"
    description:
      zh: >
          把既有文件系统镜像扩容到更大尺寸并返回新超级块。
          
      en: >
          Extend an existing filesystem image to a larger size and return the new superblock.
          
deps:
  - kind: call
    to: pyvdisk.storage.block.access
    from_api: "rpc:pyvdisk.fs.grow"
    to_api: "rpc:pyvdisk.disk.VirtualDisk#truncate_bytes"
    label: {zh: "扩大镜像", en: "enlarges image"}
---
