---
uid: a0000702
id: pyvdisk.storage.volume.model
parent: pyvdisk.storage.volume
name: {zh: "卷模型", en: "Volume Model"}
description:
  zh: >
      卷模型，以及按模式把成员容量换算为逻辑地址空间的几何计算。
  en: >
      Volume model and the geometry computation that turns member capacities into a logical address space per mode.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 125
    end_line: 179
apis:
  - protocol: rpc
    path: "pyvdisk.volume.Volume"
    description:
      zh: >
          把成员盘聚合到单一块接口后的卷对象。
      en: >
          Volume object aggregating member disks behind one block interface.
  - protocol: rpc
    path: "pyvdisk.volume.Volume#__init__"
    description:
      zh: >
          把卷绑定到成员路径与块大小。
      en: >
          Bind a volume to its member paths and block size.
  - protocol: rpc
    path: "pyvdisk.volume.Volume#compute_geometry"
    description:
      zh: >
          根据成员容量计算 concat/stripe/mirror 几何。
      en: >
          Compute concat/stripe/mirror geometry from member capacities.
---
