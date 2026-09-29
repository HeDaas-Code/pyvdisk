---
uid: a0000303
id: pyvdisk.storage.identity
parent: pyvdisk.storage
name: {zh: "磁盘身份", en: "Disk Identity"}
description:
  zh: >
      磁盘身份：block 0 末尾的 112 字节 VDID 尾标，让每块 .vdisk 不依赖路径即可被识别。
  en: >
      Disk identity: a 112-byte VDID trailer in block 0 that identifies each .vdisk file independently of its path.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 79d877b6840991d3a1de01a41018bf417b9d899c8649bb49dd7b7f5f9ed0f2ab
source:
  - path: "pyvdisk/identity.py"
---
