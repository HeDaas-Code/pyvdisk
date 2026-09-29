---
uid: a0000409
id: pyvdisk.storage.fs.inode-io
parent: pyvdisk.storage.fs
name: {zh: "Inode 表 IO", en: "Inode Table IO"}
description:
  zh: >
      inode 表 IO：128 字节 inode 记录的分配、释放与定位读写。
      
  en: >
      Inode table IO: allocation, release and positioned read/write of 128-byte inode records.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 352
    end_line: 375
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#alloc_inode"
    description:
      zh: >
          分配一个空闲 inode 号。
          
      en: >
          Allocate a free inode number.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#free_inode"
    description:
      zh: >
          释放 inode 并清除其位图位。
          
      en: >
          Release an inode and clear its bitmap bit.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#_inode_offset"
    description:
      zh: >
          计算 inode 在 inode 表中的字节偏移。
          
      en: >
          Compute the byte offset of an inode inside the inode table.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#read_inode"
    description:
      zh: >
          读取并解码一个 inode。
          
      en: >
          Read and decode one inode.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#write_inode"
    description:
      zh: >
          把一个 inode 编码后写回表。
          
      en: >
          Encode and write one inode back to the table.
          
deps:
  - kind: call
    to: pyvdisk.storage.block.access
    from_api: "rpc:pyvdisk.fs.FS#read_inode"
    to_api: "rpc:pyvdisk.disk.VirtualDisk#read_bytes"
    label: {zh: "读取 inode 表", en: "reads inode table"}
---
