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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.245Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
