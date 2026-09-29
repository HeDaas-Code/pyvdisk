---
uid: a0000205
id: pyvdisk.storage.block.access
parent: pyvdisk.storage.block
name: {zh: "块访问", en: "Block Access"}
description:
  zh: >
      已打开镜像上的块级与字节级访问：块读写、裸字节区间与镜像扩缩。
      
  en: >
      Block and byte access on an open image: block read/write, raw byte ranges and image resize.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: 88da0b2f3ce22b186edf88eab3d800c8e50671236a9ed1b9dbed478ff6837d16
source:
  - path: "pyvdisk/disk.py"
    line: 143
    end_line: 188
apis:
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#read_block"
    description:
      zh: >
          带越界检查地读取一个完整块。
          
      en: >
          Read one whole block with bounds checking.
          
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#write_block"
    description:
      zh: >
          写入一个块，不足处补零。
          
      en: >
          Write one block, zero-padding short payloads.
          
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#read_bytes"
    description:
      zh: >
          按字节偏移读取一段数据。
          
      en: >
          Read a byte range at an arbitrary offset.
          
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#write_bytes"
    description:
      zh: >
          按字节偏移写入一段数据。
          
      en: >
          Write a byte range at an arbitrary offset.
          
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#truncate_bytes"
    description:
      zh: >
          把镜像调整到整块数大小。
          
      en: >
          Resize the image to a whole number of blocks.
          
deps:
  - kind: call
    to: pyvdisk.storage.block.io
    from_api: "rpc:pyvdisk.disk.VirtualDisk#read_block"
    label: {zh: "定位读取", en: "positional read"}
  - kind: call
    to: pyvdisk.storage.block.io
    from_api: "rpc:pyvdisk.disk.VirtualDisk#write_block"
    label: {zh: "定位写入", en: "positioned write"}
---
