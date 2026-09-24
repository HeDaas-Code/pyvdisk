---
uid: a000040a
id: pyvdisk.storage.fs.block-alloc
parent: pyvdisk.storage.fs
name: {zh: "块分配器", en: "Block Allocator"}
description:
  zh: >
      建立在块位图之上的数据块分配器。
  en: >
      Data block allocator on top of the block bitmap.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 377
    end_line: 389
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#alloc_block"
    description:
      zh: >
          分配一个空闲数据块并标记为已用。
      en: >
          Allocate a free data block and mark it used.
  - protocol: rpc
    path: "pyvdisk.fs.FS#free_block"
    description:
      zh: >
          释放数据块并清除其位图位。
      en: >
          Free a data block and clear its bitmap bit.
---
