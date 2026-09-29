---
uid: 447d99b2
id: pyvdisk.tests.fuse-mount
parent: pyvdisk.tests
tags: [tests, fuse]
name: {zh: "FUSE 挂载用例", en: "FUSE Mount Tests"}
description:
  zh: >
      FUSE 桥用例：属性与目录操作、truncate/link/chmod，以及此前对任何符号链接都返回 EINVAL 的 lstat 语义 readlink。
      
  en: >
      FUSE bridge tests: attribute and directory operations, truncate/link/chmod, and the lstat-semantics readlink that used to fail every symlink with EINVAL.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.212Z"
fingerprint: b0e0301f87cd1dbd412bd5c29ce373d1bba6eb5e77134f89d377365a340a373b
source:
  - path: "tests/test_fuse_mount.py"
    line: 1
    end_line: 251
apis:
  - protocol: rpc
    path: "tests/test_fuse_mount.py"
    description:
      zh: >
          用桩 fuse 模块覆盖 FUSE 桥的 21 个用例。
          
      en: >
          21 cases over the FUSE bridge with a stub fuse module.
          
deps:
  - kind: call
    to: pyvdisk.storage.fuse.handlers
    from_api: "rpc:tests/test_fuse_mount.py"
    to_api: "rpc:pyvdisk.fuse_mount._VFuseOperations#_readlink"
    label: {zh: "验证 FUSE 操作表", en: "exercises FUSE operations"}
---
