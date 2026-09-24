---
uid: a0000706
id: pyvdisk.storage.volume.bytes
parent: pyvdisk.storage.volume
name: {zh: "字节传输", en: "Byte Transport"}
description:
  zh: >
      字节级传输、描述符复制与 CLI 使用的状态报告。
  en: >
      Byte-level transport, descriptor replication and the status report consumed by the CLI.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 375
    end_line: 477
apis:
  - protocol: rpc
    path: "pyvdisk.volume.Volume#read_bytes"
    description:
      zh: >
          跨逻辑块读取非对齐字节。
      en: >
          Read unaligned bytes across logical block boundaries.
  - protocol: rpc
    path: "pyvdisk.volume.Volume#write_bytes"
    description:
      zh: >
          跨逻辑块写入非对齐字节。
      en: >
          Write unaligned bytes across logical block boundaries.
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_write_meta_to_all"
    description:
      zh: >
          把卷描述符复制到每个成员的 block 0。
      en: >
          Replicate the volume descriptor into every member block 0.
  - protocol: rpc
    path: "pyvdisk.volume.Volume#status"
    description:
      zh: >
          报告卷模式、成员健康状况与容量汇总。
      en: >
          Report volume mode, member health and capacity summary.
---
