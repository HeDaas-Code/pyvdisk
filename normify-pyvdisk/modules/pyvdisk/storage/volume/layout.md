---
uid: a0000705
id: pyvdisk.storage.volume.layout
parent: pyvdisk.storage.volume
name: {zh: "RAID 映射", en: "RAID Mapping"}
description:
  zh: >
      分模式地址映射：拼接、条带与镜像，镜像读取支持副本回退。
      
  en: >
      Mode-specific address mapping: concatenation, striping and mirroring with replica fallback on read.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 303
    end_line: 374
apis:
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_read_concat"
    description:
      zh: >
          在 concat 成员上线性映射逻辑块。
          
      en: >
          Map a logical block linearly across concat members.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_write_concat"
    description:
      zh: >
          在拼接位置写入一个块。
          
      en: >
          Write one block at its concatenated position.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_stripe_locate"
    description:
      zh: >
          定位条带化逻辑块所属成员与成员内偏移。
          
      en: >
          Locate the member and intra-member offset of a striped logical block.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_read_stripe"
    description:
      zh: >
          读取一个条带块。
          
      en: >
          Read one striped block.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_write_stripe"
    description:
      zh: >
          写入一个条带块。
          
      en: >
          Write one striped block.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_read_mirror"
    description:
      zh: >
          读取镜像块，副本损坏时回退到存活副本。
          
      en: >
          Read a mirrored block, falling back to a surviving replica.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_write_mirror"
    description:
      zh: >
          把镜像块写入每个副本。
          
      en: >
          Write a mirrored block to every replica.
          
deps:
  - kind: dataflow
    to: pyvdisk.storage.volume.blocks
    from_api: "rpc:pyvdisk.volume.Volume#_read_mirror"
    to_api: "rpc:pyvdisk.volume.Volume#read_block"
    label: {zh: "读取成员", en: "reads members"}
---
