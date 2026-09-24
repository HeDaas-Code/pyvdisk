---
uid: a0000d03
id: pyvdisk.tests.vdisk.names
parent: pyvdisk.tests.vdisk
name: {zh: "命名空间用例", en: "Namespace Tests"}
description:
  zh: >
      命名空间语义：重命名、符号链接与文件对象接口。
  en: >
      Namespace semantics: rename, symbolic links and the file-object interface.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 152
    end_line: 240
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestRename"
    description:
      zh: >
          文件与目录重命名，含覆盖与顺序。
      en: >
          File and directory rename including overwrite and ordering.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestSymlink"
    description:
      zh: >
          符号链接创建、路径解析、环路检测与相对目标。
      en: >
          Symlink creation, path resolution, loop detection and relative targets.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestVFile"
    description:
      zh: >
          VFile 的读/写/seek/append 语义。
      en: >
          VFile read/write/seek/append semantics.
---
