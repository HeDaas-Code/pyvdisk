---
uid: a0000208
id: pyvdisk.storage.identity.trailer
parent: pyvdisk.storage.identity
name: {zh: "尾标编解码", en: "Trailer Codec"}
description:
  zh: >
      身份尾标的二进制编解码：定长 112 字节布局的打包与解析。
      
  en: >
      Binary codec for the identity trailer: pack and parse the fixed-width 112-byte layout.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 79d877b6840991d3a1de01a41018bf417b9d899c8649bb49dd7b7f5f9ed0f2ab
source:
  - path: "pyvdisk/identity.py"
    line: 56
    end_line: 113
apis:
  - protocol: rpc
    path: "pyvdisk.identity.make_trailer"
    description:
      zh: >
          把 disk_uuid、vol_id、label 与 flags 打包成 112 字节尾标。
          
      en: >
          Pack disk_uuid, vol_id, label and flags into the 112-byte trailer.
          
  - protocol: rpc
    path: "pyvdisk.identity.parse_trailer"
    description:
      zh: >
          从块尾解析尾标；魔数不匹配时返回 None。
          
      en: >
          Parse the trailer from a block; returns None when the magic does not match.
          
deps:
  - kind: call
    to: pyvdisk.storage.identity.model
    from_api: "rpc:pyvdisk.identity.parse_trailer"
    to_api: "rpc:pyvdisk.identity.DiskIdentity"
    label: {zh: "构造身份模型", en: "builds identity model"}
---
