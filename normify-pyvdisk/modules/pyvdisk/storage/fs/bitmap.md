---
uid: a0000408
id: pyvdisk.storage.fs.bitmap
parent: pyvdisk.storage.fs
name: {zh: "位图分配", en: "Bitmap Allocation"}
description:
  zh: >
      inode 与数据块分配共用的位图原语。
  en: >
      Bitmap primitives shared by inode and data-block allocation.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 320
    end_line: 350
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#_bitmap_get"
    description:
      zh: >
          测试盘上位图区域中的某一位。
      en: >
          Test one bit in an on-disk bitmap region.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_bitmap_set"
    description:
      zh: >
          设置或清除盘上位图区域中的某一位。
      en: >
          Set or clear one bit in an on-disk bitmap region.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_bitmap_alloc"
    description:
      zh: >
          在位图区域中查找首个空闲位（可从提示位开始）。
      en: >
          Find the first free bit in a bitmap region, optionally from a hint.
---
