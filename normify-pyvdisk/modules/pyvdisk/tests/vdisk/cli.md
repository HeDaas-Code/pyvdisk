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
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.242Z"
fingerprint: 3855e965b1d64d49d91e1f55344fdf67a6ec626f3493b5cb3a5fd8c83bc6e9cf
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
