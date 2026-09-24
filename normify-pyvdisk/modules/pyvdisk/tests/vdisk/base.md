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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
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
