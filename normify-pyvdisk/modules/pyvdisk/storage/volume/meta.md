---
uid: a0000701
id: pyvdisk.storage.volume.meta
parent: pyvdisk.storage.volume
name: {zh: "卷元数据", en: "Volume Metadata"}
description:
  zh: >
      卷元数据模型：写入每个成员的描述符及其内部的成员记录。
  en: >
      Volume metadata model: the descriptor written into every member and the member records inside it.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 41
    end_line: 123
apis:
  - protocol: rpc
    path: "pyvdisk.volume.VolumeError"
    description:
      zh: >
          卷几何、成员与模式错误时抛出。
      en: >
          Raised for volume geometry, member and mode failures.
  - protocol: rpc
    path: "pyvdisk.volume.DiskMember"
    description:
      zh: >
          单个成员盘：序号、UUID、路径、块数与角色标志。
      en: >
          One member disk: index, uuid, path, block count and role flags.
  - protocol: rpc
    path: "pyvdisk.volume.VolumeMeta"
    description:
      zh: >
          卷描述符：名称、模式、块大小、成员表与几何。
      en: >
          Volume descriptor: name, mode, block size, member list and geometry.
  - protocol: rpc
    path: "pyvdisk.volume.VolumeMeta#to_bytes"
    description:
      zh: >
          把卷描述符序列化，供存入成员 block 0。
      en: >
          Serialize the volume descriptor for storage in member block 0.
  - protocol: rpc
    path: "pyvdisk.volume.VolumeMeta#from_bytes"
    description:
      zh: >
          解析已存卷描述符并校验成员布局。
      en: >
          Parse a stored volume descriptor and validate its member layout.
---
