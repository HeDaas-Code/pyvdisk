---
uid: a0000d01
id: pyvdisk.tests.vdisk.base
parent: pyvdisk.tests.vdisk
name: {zh: "VFS 测试基类", en: "VFS Test Base"}
description:
  zh: >
      测试基类与基础路径用例：启动镜像的夹具，以及最小的 VFS 行为。
      
  en: >
      Test base and the basic-path suite: the fixture that boots an image, plus the smallest VFS behaviours.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.242Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
source:
  - path: "tests/test_vdisk.py"
    line: 19
    end_line: 78
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::VFSTestBase"
    description:
      zh: >
          为每个用例创建临时镜像并挂载 VFS 的共享夹具。
          
      en: >
          Shared fixture that creates a temporary image and mounts a VFS for each test.
          
  - protocol: rpc
    path: "tests/test_vdisk.py::TestBasic"
    description:
      zh: >
          根目录、mkdir、makedirs、小文件写、覆盖与追加重为。
          
      en: >
          Root directory, mkdir, makedirs, small write, overwrite and append behaviour.
          
---
