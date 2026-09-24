---
uid: a000020a
id: pyvdisk.storage.identity.probe
parent: pyvdisk.storage.identity
name: {zh: "身份探测", en: "Identity Probe"}
description:
  zh: >
      身份 IO：写尾标、不挂载即探测盘文件，以及 UUID 生成。
      
  en: >
      Identity IO: writing the trailer, probing a disk file without mounting it, and uuid generation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: 79d877b6840991d3a1de01a41018bf417b9d899c8649bb49dd7b7f5f9ed0f2ab
source:
  - path: "pyvdisk/identity.py"
    line: 159
    end_line: 226
apis:
  - protocol: rpc
    path: "pyvdisk.identity.write_identity_to_block0"
    description:
      zh: >
          以读-改-写方式把身份尾标写入 block 0 末尾。
          
      en: >
          Read-modify-write the identity trailer at the end of block 0.
          
  - protocol: rpc
    path: "pyvdisk.identity.probe_disk"
    description:
      zh: >
          探测一个 .vdisk 文件，判定其为成员盘、单盘、向量盘、日志盘或未知。
          
      en: >
          Probe one .vdisk file and classify it as member, single, vector, log or unknown.
          
  - protocol: rpc
    path: "pyvdisk.identity.new_disk_uuid"
    description:
      zh: >
          生成新的随机磁盘 UUID。
          
      en: >
          Generate a new random disk uuid.
          
deps:
  - kind: call
    to: pyvdisk.storage.identity.trailer
    from_api: "rpc:pyvdisk.identity.probe_disk"
    to_api: "rpc:pyvdisk.identity.parse_trailer"
    label: {zh: "解析尾标", en: "parses trailer"}
---
