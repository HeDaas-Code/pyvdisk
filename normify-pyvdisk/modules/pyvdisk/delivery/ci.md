---
uid: a000010a
id: pyvdisk.delivery.ci
parent: pyvdisk.delivery
name: {zh: "测试工作流", en: "Test Workflow"}
description:
  zh: >
      CI 工作流：在 push 与 pull request 上安装 dev extras 并运行 pytest 套件。
  en: >
      CI workflow that installs the package with dev extras and runs the pytest suite on push and pull request.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 0a0bcf375716cce59392d0ac9fcc4ece1907ceb1089749522f9738787e500b34
source:
  - path: ".github/workflows/ci.yml"
apis:
  - protocol: file
    path: ".github/workflows/ci.yml"
    description:
      zh: >
          主测试工作流：安装依赖并运行 pytest 套件。
      en: >
          Main test workflow: install and run the pytest suite.
---
