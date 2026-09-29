---
uid: a0000e08
id: pyvdisk.tests.atomic-save
parent: pyvdisk.tests
name: {zh: "原子保存用例", en: "Atomic Save Tests"}
description:
  zh: >
      验证元数据写入是全有或全无，即事务层所依赖的性质。
      
  en: >
      Verifies that metadata writes are all-or-nothing, the property the transaction layer is built on.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: ef2c08e8d92ecaf62dcb22be9753adaa7e64ca008d860af041310eeb8f56b0da
source:
  - path: "tests/test_atomic_vfs_save.py"
apis:
  - protocol: rpc
    path: "tests/test_atomic_vfs_save.py"
    description:
      zh: >
          含中断场景的 VFS 原子保存行为。
          
      en: >
          Atomic VFS save behaviour including interruption.
          
deps:
  - kind: call
    to: pyvdisk.storage.datadisk.core
    to_api: "rpc:pyvdisk.infrastructure.disk.DataDisk#_atomic_json"
    label: {zh: "验证原子写入", en: "verifies atomic write"}
---
