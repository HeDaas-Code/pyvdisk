---
uid: a0000413
id: pyvdisk.storage.fs.truncate
parent: pyvdisk.storage.fs
name: {zh: "截断", en: "Truncate"}
description:
  zh: >
      截断操作及其后续的间接块清理。
  en: >
      Truncation and the indirect-block cleanup that follows it.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 948
    end_line: 1015
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#truncate"
    description:
      zh: >
          调整 inode 尺寸，增长时补零、收缩时释放块。
      en: >
          Resize an inode, zero-filling growth and releasing blocks on shrink.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_clear_block_ptr"
    description:
      zh: >
          清除一个逻辑块指针并释放其数据块。
      en: >
          Clear one logical block pointer and free its block.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_maybe_free_indirect"
    description:
      zh: >
          在截断后释放不再需要的间接块。
      en: >
          Release indirect blocks that are no longer needed after a truncate.
---
