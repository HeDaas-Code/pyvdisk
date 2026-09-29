---
uid: a000033f
id: pyvdisk.tests.agent-sandbox
parent: pyvdisk.tests
name: {zh: "沙箱测试", en: "Sandbox Tests"}
description:
  zh: >
      把 AgentSandbox 当作一组承诺来测，而不是按实现来测：越权路径、Windows 样式路径、被隐藏的容器簿记、只读与禁删模式、含伪造行的审计链、脚本的宿主隔离与输出上限、"脚本入口与 Python 入口共用一个根"这条规则，以及防止 README 示例漂移、确保它仍能按真实 API 执行的守卫。
      
  en: >
      Tests AgentSandbox as a set of promises rather than an implementation: escape attempts, Windows-looking paths, hidden bookkeeping, read-only and no-delete modes, the audit trail including forged rows, script host isolation and output caps, the rule that the script door and the Python door share one root, and guards that keep the README demo executing against the real API.
      
revision: f163400c098f68cbdfb0393a9bf488037d012aaf
updated_at: "2026-09-24T11:48:38.687Z"
fingerprint: e44e25577e09fe09eef14d1d56de5975ad490fb995cfce45029bb93e2768012e
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
