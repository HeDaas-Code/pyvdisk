---
uid: a0000414
id: pyvdisk.storage.fs.query
parent: pyvdisk.storage.fs
name: {zh: "状态与空间查询", en: "Stat and Space Queries"}
description:
  zh: >
      只读查询：stat 变体、空闲对象计数，以及 df/du 使用的 statfs 汇总。
  en: >
      Read-only queries: stat variants, free-object counts and the statfs summary consumed by df/du.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 1018
    end_line: 1078
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#stat"
    description:
      zh: >
          按 inode 号取 stat。
      en: >
          Stat an inode by number.
  - protocol: rpc
    path: "pyvdisk.fs.FS#stat_path"
    description:
      zh: >
          按路径取 stat，可选是否跟踪末尾符号链接。
      en: >
          Stat a path, optionally following the final symlink.
  - protocol: rpc
    path: "pyvdisk.fs.FS#lstat_path"
    description:
      zh: >
          不跟踪末尾符号链接地取 stat。
      en: >
          Stat a path without following the final symlink.
  - protocol: rpc
    path: "pyvdisk.fs.FS#count_free_blocks"
    description:
      zh: >
          统计空闲数据块。
      en: >
          Count free data blocks.
  - protocol: rpc
    path: "pyvdisk.fs.FS#count_free_inodes"
    description:
      zh: >
          统计空闲 inode。
      en: >
          Count free inodes.
  - protocol: rpc
    path: "pyvdisk.fs.FS#statfs"
    description:
      zh: >
          报告文件系统几何与剩余空间统计。
      en: >
          Report filesystem geometry and free-space statistics.
---
