---
uid: a000010b
id: pyvdisk.delivery.lint
parent: pyvdisk.delivery
name: {zh: "静态分析工作流", en: "Lint Workflow"}
description:
  zh: >
      独立于单元测试门禁的静态分析流水线，运行 pylint。
  en: >
      Workflow running pylint as a static-analysis gate separate from the unit-test gate.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 6e6bddfc03853c3f31fb6155a5820cd230812d5e35704de2e01fc1f9541ff6f2
source:
  - path: ".github/workflows/pylint.yml"
apis:
  - protocol: file
    path: ".github/workflows/pylint.yml"
    description:
      zh: >
          静态分析工作流：对包运行 pylint。
      en: >
          Static-analysis workflow: run pylint over the package.
---
