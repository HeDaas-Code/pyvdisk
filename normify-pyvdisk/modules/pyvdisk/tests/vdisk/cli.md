---
uid: a0000d08
id: pyvdisk.tests.vdisk.cli
parent: pyvdisk.tests.vdisk
name: {zh: "CLI 用例", en: "CLI Tests"}
description:
  zh: >
      CLI 契约用例：以用户方式调用每个子命令并断言其输出形态。
  en: >
      The CLI contract test: every subcommand is invoked the way a user would and its output shape asserted.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 8c9616395f1cb1647444cd364eeb44d4c9f2a723f3162a8421918c81c6cd4556
source:
  - path: "tests/test_vdisk.py"
    line: 536
    end_line: 670
apis:
  - protocol: rpc
    path: "tests/test_vdisk.py::TestCLI"
    description:
      zh: >
          驱动 argparse 接口的端到端 CLI 子命令用例。
      en: >
          End-to-end CLI subcommand tests driving the argparse surface.
---
