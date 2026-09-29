---
uid: a0000209
id: pyvdisk.storage.identity.model
parent: pyvdisk.storage.identity
name: {zh: "身份模型", en: "Identity Model"}
description:
  zh: >
      DiskIdentity 值对象及其类型判定与简短展示形式。
  en: >
      DiskIdentity value object plus its kind predicates and short display form.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 79d877b6840991d3a1de01a41018bf417b9d899c8649bb49dd7b7f5f9ed0f2ab
source:
  - path: "pyvdisk/identity.py"
    line: 116
    end_line: 156
apis:
  - protocol: rpc
    path: "pyvdisk.identity.DiskIdentity"
    description:
      zh: >
          身份记录：类型、磁盘 UUID、卷 ID、卷标、标志位与可选卷元数据。
      en: >
          Identity record: kind, disk uuid, volume id, label, flags and optional volume metadata.
  - protocol: rpc
    path: "pyvdisk.identity.DiskIdentity#is_single"
    description:
      zh: >
          该盘是独立文件系统镜像时为真。
      en: >
          True when the disk is a standalone filesystem image.
  - protocol: rpc
    path: "pyvdisk.identity.DiskIdentity#is_complete_member"
    description:
      zh: >
          该盘为成员盘且卷元数据已成功解析时为真。
      en: >
          True when the disk is a volume member whose volume metadata parsed.
  - protocol: rpc
    path: "pyvdisk.identity.DiskIdentity#short"
    description:
      zh: >
          紧凑的人类可读身份摘要。
      en: >
          Compact human-readable identity summary.
---
