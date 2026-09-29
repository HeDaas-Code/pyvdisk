---
uid: a0000407
id: pyvdisk.storage.fs.mount
parent: pyvdisk.storage.fs
name: {zh: "挂载", en: "Mount"}
description:
  zh: >
      FS 构造、挂载时超级块校验与超级块持久化。
      
  en: >
      FS construction, mount-time superblock validation and superblock persistence.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 273
    end_line: 318
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS"
    description:
      zh: >
          绑定到单个块设备的文件系统；持有超级块与共享锁。
          
      en: >
          Filesystem bound to one block device; holds the superblock and shared lock.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#mount"
    description:
      zh: >
          挂载文件系统并校验盘上超级块。
          
      en: >
          Mount the filesystem and validate the on-disk superblock.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#flush_superblock"
    description:
      zh: >
          把内存中的超级块写回 block 0。
          
      en: >
          Persist the in-memory superblock back to block 0.
          
deps:
  - kind: call
    to: pyvdisk.storage.block.access
    from_api: "rpc:pyvdisk.fs.FS#mount"
    to_api: "rpc:pyvdisk.disk.VirtualDisk#read_block"
    label: {zh: "读取 block 0", en: "reads block 0"}
---
