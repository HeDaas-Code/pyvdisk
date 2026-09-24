---
uid: a0000704
id: pyvdisk.storage.volume.blocks
parent: pyvdisk.storage.volume
name: {zh: "逻辑块", en: "Logical Blocks"}
description:
  zh: >
      按模式分发到具体地址映射的逻辑块入口。
      
  en: >
      Logical block entry points that dispatch to the mode-specific address mapping.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 260
    end_line: 302
apis:
  - protocol: rpc
    path: "pyvdisk.volume.Volume#truncate_bytes"
    description:
      zh: >
          调整逻辑卷及每个成员的尺寸。
          
      en: >
          Resize the logical volume and every member.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#read_block"
    description:
      zh: >
          按当前模式读取一个逻辑块。
          
      en: >
          Read one logical block through the active mode.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#write_block"
    description:
      zh: >
          按当前模式写入一个逻辑块。
          
      en: >
          Write one logical block through the active mode.
          
---
