---
uid: a000040e
id: pyvdisk.storage.fs.paths
parent: pyvdisk.storage.fs
name: {zh: "路径解析", en: "Path Resolution"}
description:
  zh: >
      路径解析：分量拆分、带深度上限的符号链接感知查找，以及创建所需的父目录解析。
      
  en: >
      Path resolution: component splitting, symlink-aware lookup with a depth bound, and parent resolution for creation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 588
    end_line: 641
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#_split_path"
    description:
      zh: >
          把 POSIX 路径拆分为非空分量。
          
      en: >
          Split a POSIX path into non-empty components.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#resolve"
    description:
      zh: >
          把路径解析为 inode 号，跟踪符号链接并限制深度。
          
      en: >
          Resolve a path to an inode number, following symlinks and bounding depth.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#resolve_parent"
    description:
      zh: >
          把路径解析为父目录 inode 与末段名字。
          
      en: >
          Resolve a path to its parent directory inode and final name.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.dir
    from_api: "rpc:pyvdisk.fs.FS#resolve"
    to_api: "rpc:pyvdisk.fs.FS#dir_lookup"
    label: {zh: "逐级遍历目录", en: "walks directories"}
---
