---
uid: a0000405
id: pyvdisk.storage.fs.inode
parent: pyvdisk.storage.fs
name: {zh: "Inode", en: "Inode"}
description:
  zh: >
      inode 结构及其二进制编解码与空节点工厂。
  en: >
      Inode structure with its binary codec and empty-node factory.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 157
    end_line: 226
apis:
  - protocol: rpc
    path: "pyvdisk.fs.Inode"
    description:
      zh: >
          inode 值对象：类型、模式、链接数、属主、时间戳、尺寸与块指针。
      en: >
          Inode value object: type, mode, links, ownership, timestamps, size and block pointers.
  - protocol: rpc
    path: "pyvdisk.fs.Inode#to_bytes"
    description:
      zh: >
          把 inode 序列化为 101 字节打包形式。
      en: >
          Serialize the inode into its 101-byte packed form.
  - protocol: rpc
    path: "pyvdisk.fs.Inode#from_bytes"
    description:
      zh: >
          从打包字节解析 inode。
      en: >
          Parse an inode from its packed bytes.
  - protocol: rpc
    path: "pyvdisk.fs.Inode#empty"
    description:
      zh: >
          构造指针全零的空 inode。
      en: >
          Build an empty inode with zeroed pointers.
---
