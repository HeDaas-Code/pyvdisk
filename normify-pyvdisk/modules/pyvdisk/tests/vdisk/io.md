---
uid: a0000d04
id: pyvdisk.tests.vdisk.io
parent: pyvdisk.tests.vdisk
name: {zh: "持久性与 IO 用例", en: "Persistence and IO Tests"}
description:
  zh: >
      持久性与 IO 边界用例：重挂载持久性、宿主传输与非法路径错误。
  en: >
      Durability and IO boundary tests: remount persistence, host transfer and invalid-path errors.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 241
    end_line: 319
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestPersistence"
    description:
      zh: >
          重新挂载后数据与结构的持久性。
      en: >
          Remount persistence of data and structure.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestImportExport"
    description:
      zh: >
          宿主文件与目录树的导入导出。
      en: >
          Host import and export of files and trees.
  - protocol: rpc
    path: "tests/test_vdisk.py::TestEdgeCases"
    description:
      zh: >
          缺失或非法路径的错误与边界用例。
      en: >
          Error and boundary cases for missing or invalid paths.
---
