---
uid: a0000f01
id: pyvdisk.compat.unified
parent: pyvdisk.compat
tags: [compat]
name: {zh: "Unified 别名", en: "Unified Aliases"}
description:
  zh: >
      兼容重导出：保留容器化之前的 DataDisk 与 MetadataTransaction 导入路径。
  en: >
      Compatibility re-exports that keep the pre-container DataDisk and MetadataTransaction import paths working.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7bd0da8459e2672fd8efee93a3734b6ed45da3af20763bc82dabc158f892e87d
source:
  - path: "pyvdisk/unified.py"
apis:
  - protocol: rpc
    path: "pyvdisk.unified.DataDisk"
    description:
      zh: >
          保留旧 Unified 容器名称可导入的兼容别名。
      en: >
          Legacy alias keeping the old Unified container name importable.
  - protocol: rpc
    path: "pyvdisk.unified.MetadataTransaction"
    description:
      zh: >
          元数据事务类型的兼容别名。
      en: >
          Legacy alias for the metadata transaction type.
---
