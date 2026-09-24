---
uid: a000033f
id: pyvdisk.tests.agent-sandbox
parent: pyvdisk.tests
name: {zh: "沙箱测试", en: "Sandbox Tests"}
description:
  zh: >
      把 AgentSandbox 当作一组承诺来测，而不是按实现来测：越权路径、Windows 样式路径、被隐藏的容器簿记、只读与禁删模式、含伪造行的审计链、脚本的宿主隔离与输出上限，以及"脚本入口与 Python 入口共用一个根"这条规则。
  en: >
      Tests AgentSandbox as a set of promises rather than an implementation: escape attempts, Windows-looking paths, hidden bookkeeping, read-only and no-delete modes, the audit trail including forged rows, script host isolation and output caps, and the rule that the script door and the Python door share one root.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: edf41d7c5682215a34e651deccb8a108c248aad110293e0dd67c0e56a01c7290
source:
  - path: "tests/test_agent_sandbox.py"
apis:
  - protocol: file
    path: "tests/test_agent_sandbox.py"
    description:
      zh: >
          沙箱的承诺：路径约束、只读、审计链与脚本隔离。
      en: >
          Sandbox promises: path confinement, read-only, audit chain and script isolation.
---
