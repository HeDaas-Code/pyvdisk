---
uid: a000040c
id: pyvdisk.storage.fs.dir
parent: pyvdisk.storage.fs
name: {zh: "目录读取", en: "Directory Read"}
description:
  zh: >
      目录读取路径：目录项解码、列举与按名查找。
  en: >
      Directory read path: entry decoding, listing and name lookup.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 490
    end_line: 522
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#_dir_entries_block"
    description:
      zh: >
          解码某个数据块中存储的全部有效目录项。
      en: >
          Decode all valid directory entries stored in one data block.
  - protocol: rpc
    path: "pyvdisk.fs.FS#dir_list"
    description:
      zh: >
          列出目录中的名字、inode 与类型三元组。
      en: >
          List name, inode and type triples in a directory.
  - protocol: rpc
    path: "pyvdisk.fs.FS#dir_lookup"
    description:
      zh: >
          在目录中查找单个名字。
      en: >
          Look up one name in a directory.
---
