---
uid: a0000708
id: pyvdisk.storage.volume.repair
parent: pyvdisk.storage.volume
name: {zh: "镜像维护", en: "Mirror Maintenance"}
description:
  zh: >
      在线镜像维护：新增、移除与重新同步副本。
      
  en: >
      Online mirror maintenance: add, remove and resynchronize replicas.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 558
    end_line: 648
apis:
  - protocol: rpc
    path: "pyvdisk.volume.add_mirror"
    description:
      zh: >
          不中断卷使用地新增镜像成员。
          
      en: >
          Add a mirror member without interrupting the volume.
          
  - protocol: rpc
    path: "pyvdisk.volume.remove_mirror"
    description:
      zh: >
          确认剩余副本充足后移除镜像成员。
          
      en: >
          Remove a mirror member after verifying the remaining replicas.
          
  - protocol: rpc
    path: "pyvdisk.volume.resync_mirror"
    description:
      zh: >
          以权威副本重新同步镜像成员。
          
      en: >
          Resynchronize mirror members from the authoritative copy.
          
deps:
  - kind: call
    to: pyvdisk.storage.volume.open
    from_api: "rpc:pyvdisk.volume.resync_mirror"
    to_api: "rpc:pyvdisk.volume.Volume#open"
    label: {zh: "重开卷", en: "reopens volume"}
---
