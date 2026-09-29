---
uid: a0000403
id: pyvdisk.storage.fs.names
parent: pyvdisk.storage.fs
name: {zh: "名字编解码", en: "Name Codec"}
description:
  zh: >
      目录槽位名编解码，以及跨文件系统接口使用的 FSError。
  en: >
      Name codec for directory slots plus the FSError type used across the filesystem surface.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 254
    end_line: 270
apis:
  - protocol: rpc
    path: "pyvdisk.fs._encode_name"
    description:
      zh: >
          把目录名编码进固定的 27 字节槽位。
      en: >
          Encode a directory name into the fixed 27-byte slot.
  - protocol: rpc
    path: "pyvdisk.fs._decode_name"
    description:
      zh: >
          解码定宽目录名槽位。
      en: >
          Decode a fixed-width directory name slot.
  - protocol: rpc
    path: "pyvdisk.fs._ceil_div"
    description:
      zh: >
          整数向上取整除法。
      en: >
          Integer ceiling division helper.
  - protocol: rpc
    path: "pyvdisk.fs.FSError"
    description:
      zh: >
          路径非法或元数据损坏时抛出的文件系统错误。
      en: >
          Filesystem-level error raised for invalid paths and corrupted metadata.
---
