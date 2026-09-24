---
uid: a0000415
id: pyvdisk.storage.fs.fsck
parent: pyvdisk.storage.fs
name: {zh: "一致性检查", en: "Filesystem Check"}
description:
  zh: >
      一致性检查器：校验超级块、交叉核对 inode 与块位图、链接数与目录项，并支持修复模式。
  en: >
      Consistency checker: validates superblock, cross-checks inode and block bitmaps, link counts and directory entries, with an optional repair mode.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 1080
    end_line: 1194
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#fsck"
    description:
      zh: >
          检查文件系统一致性，可选修复发现的问题。
      en: >
          Check filesystem consistency, optionally repairing what is found.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_fsck_impl"
    description:
      zh: >
          扫描超级块、位图、inode 链接与目录项并产出报告。
      en: >
          Scan superblock, bitmaps, inode links and directory entries and produce a report.
---
