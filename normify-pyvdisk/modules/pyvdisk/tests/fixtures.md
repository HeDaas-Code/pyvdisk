---
uid: a0000e01
id: pyvdisk.tests.fixtures
parent: pyvdisk.tests
name: {zh: "测试夹具", en: "Test Fixtures"}
description:
  zh: >
      全套件各测试模块共享的 pytest 夹具定义。
  en: >
      Pytest fixture definitions shared by every test module in the suite.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: b09095c4826eb664908a6c15f6dd731ee5dfc3755c806adcd1cc02f1312b5330
source:
  - path: "tests/conftest.py"
apis:
  - protocol: rpc
    path: "tests/conftest.py"
    description:
      zh: >
          共享 pytest 夹具：临时镜像路径、挂载与磁盘辅助。
      en: >
          Shared pytest fixtures: temporary image paths, mounts and disk helpers.
---
