---
uid: a0000404
id: pyvdisk.storage.fs.superblock
parent: pyvdisk.storage.fs
name: {zh: "超级块", en: "Superblock"}
description:
  zh: >
      超级块结构及其二进制编解码；镜像上所有区域偏移的唯一事实来源。
  en: >
      Superblock structure and its binary codec; the single source of truth for every region offset on the image.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 111
    end_line: 155
apis:
  - protocol: rpc
    path: "pyvdisk.fs.SuperBlock"
    description:
      zh: >
          描述全部区域偏移与几何的超级块值对象。
      en: >
          Superblock value object describing all region offsets and geometry.
  - protocol: rpc
    path: "pyvdisk.fs.SuperBlock#to_bytes"
    description:
      zh: >
          把超级块序列化为打包表示。
      en: >
          Serialize the superblock into its packed representation.
  - protocol: rpc
    path: "pyvdisk.fs.SuperBlock#from_bytes"
    description:
      zh: >
          解析超级块并校验魔数与版本。
      en: >
          Parse a superblock and validate its magic and version.
---
