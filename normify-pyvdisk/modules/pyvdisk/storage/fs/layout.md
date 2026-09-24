---
uid: a0000402
id: pyvdisk.storage.fs.layout
parent: pyvdisk.storage.fs
name: {zh: "盘上布局", en: "On-Disk Layout"}
description:
  zh: >
      盘上布局常量：魔数、版本、inode 与目录项几何，以及推导出的文件尺寸上限。
  en: >
      On-disk layout constants: magic, version, inode and directory entry geometry and the derived file-size ceiling.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 81
    end_line: 107
apis:
  - protocol: rpc
    path: "pyvdisk.fs.MAGIC"
    description:
      zh: >
          文件系统魔数 VDK1。
      en: >
          Filesystem magic bytes VDK1.
  - protocol: rpc
    path: "pyvdisk.fs.VERSION"
    description:
      zh: >
          盘上文件系统格式版本。
      en: >
          On-disk filesystem format version.
  - protocol: rpc
    path: "pyvdisk.fs.INODE_SIZE"
    description:
      zh: >
          inode 打包尺寸（字节）。
      en: >
          Packed inode size in bytes.
  - protocol: rpc
    path: "pyvdisk.fs.DIRECT_COUNT"
    description:
      zh: >
          每个 inode 的直接块指针数。
      en: >
          Number of direct block pointers per inode.
  - protocol: rpc
    path: "pyvdisk.fs.MAX_FILE_SIZE"
    description:
      zh: >
          由直接加单/双间接指针决定的最大文件尺寸。
      en: >
          Maximum representable file size given direct plus single and double indirect pointers.
---
