---
uid: a000040d
id: pyvdisk.storage.fs.dir-mutate
parent: pyvdisk.storage.fs
name: {zh: "目录写入", en: "Directory Write"}
description:
  zh: >
      目录写入路径：槽位查找、目录项插入与删除。
  en: >
      Directory write path: slot search, entry insertion and entry removal.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 524
    end_line: 586
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#_find_free_dir_slot"
    description:
      zh: >
          查找空闲目录项槽位，必要时扩展目录块。
      en: >
          Find a free directory-entry slot, growing the directory block when needed.
  - protocol: rpc
    path: "pyvdisk.fs.FS#dir_add_entry"
    description:
      zh: >
          向目录添加名字到 inode 的映射。
      en: >
          Add a name-to-inode entry into a directory.
  - protocol: rpc
    path: "pyvdisk.fs.FS#dir_remove_entry"
    description:
      zh: >
          从目录删除名字并返回被删除的目录项。
      en: >
          Remove a name from a directory and return the removed entry.
---
