---
uid: a000010b
id: pyvdisk.delivery.lint
parent: pyvdisk.delivery
name: {zh: "静态分析工作流", en: "Lint Workflow"}
description:
  zh: >
      独立于单元测试门禁的静态分析流水线：pylint 只保留 error 类，使 Lint 失败不会被误认为测试失败。
      
  en: >
      Static analysis pipeline, independent of the unit-test gate: pylint with the error class only, so a lint failure can never be mistaken for a test failure.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.216Z"
fingerprint: b8b7a5b39cc8e23ea498ca698d6446ab567057a9fe91d2088fb0b05d8f95e2ac
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
