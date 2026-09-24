---
uid: a0000a07
id: pyvdisk.vscript.policy.budget
parent: pyvdisk.vscript.policy
name: {zh: "策略与预算", en: "Policy and Budget"}
description:
  zh: >
      脚本的资源治理：声明式限额与执行计费并强制限额的运行时计数器。
  en: >
      Resource governance for scripts: the declarative limits and the runtime counter that enforces them.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: ff47ac976336485cb37963fa8268f69553eddc1f28f20df0efb89166391276a6
source:
  - path: "pyvdisk/vscript/policy.py"
    line: 9
    end_line: 36
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Policy"
    description:
      zh: >
          执行策略：调用深度、循环、IO 与 Host 传输限额。
      en: >
          Execution policy: call depth, loop, IO and host-transfer limits.
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Budget"
    description:
      zh: >
          解释器计费的单次运行预算计数器。
      en: >
          Per-run budget counter charged by the interpreter.
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Budget#tick"
    description:
      zh: >
          向预算计入一个解释器步骤。
      en: >
          Charge one interpreter step against the budget.
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Budget#charge_read"
    description:
      zh: >
          向预算计入读取字节。
      en: >
          Charge read bytes against the budget.
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Budget#charge_write"
    description:
      zh: >
          向预算计入写入字节。
      en: >
          Charge written bytes against the budget.
  - protocol: rpc
    path: "pyvdisk.vscript.policy.Budget#charge_output"
    description:
      zh: >
          向预算计入产出字节。
      en: >
          Charge produced output bytes against the budget.
---
