---
uid: a0000412
id: pyvdisk.storage.fs.readwrite
parent: pyvdisk.storage.fs
name: {zh: "文件读写", en: "File Read and Write"}
description:
  zh: >
      文件数据路径：定位读取、追加、覆盖与按需分配块的偏移写入。
      
  en: >
      File data path: positional read, append, overwrite and offset write with on-demand block allocation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 860
    end_line: 946
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#read_file"
    description:
      zh: >
          从 inode 读取一段字节。
          
      en: >
          Read a byte range from an inode.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#append_path"
    description:
      zh: >
          向路径追加字节，不存在时创建文件。
          
      en: >
          Append bytes to a path, creating the file when absent.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#write_path"
    description:
      zh: >
          用给定字节覆盖写入路径。
          
      en: >
          Overwrite a path with the given bytes.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#write_file"
    description:
      zh: >
          按字节偏移写入 inode，按需分配数据块。
          
      en: >
          Write bytes into an inode at a byte offset, allocating blocks as needed.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.pointers
    from_api: "rpc:pyvdisk.fs.FS#write_file"
    to_api: "rpc:pyvdisk.fs.FS#_ensure_block_ptr"
    label: {zh: "扩展块映射", en: "extends block map"}
---
