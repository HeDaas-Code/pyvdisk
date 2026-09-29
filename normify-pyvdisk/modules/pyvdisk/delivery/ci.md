---
uid: a000010a
id: pyvdisk.delivery.ci
parent: pyvdisk.delivery
name: {zh: "测试工作流", en: "Test Workflow"}
description:
  zh: >
      CI 工作流：安装 dev 与 vector extras，在 push 与 pull request 上跨 3.9–3.12 矩阵跑 pytest，让声明的 requires-python 下限由最老的矩阵任务强制而不是靠假设。另有独立任务只装基础包并断言加速器确实缺席，零依赖的承诺因此不是自说自话。
  en: >
      CI workflow: installs the dev and vector extras and runs pytest on push and pull request across the 3.9-3.12 matrix, so the declared requires-python floor is enforced by the oldest job rather than assumed. A second job installs the package without extras and asserts the accelerators are absent, which keeps the zero-dependency claim honest.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: 2bf7b99f2ff50585631ea75453ea75cc457a6fe7bece3d39c4fd4b40d5eadc13
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
  - protocol: file
    path: ".github/workflows/ci.yml#no-dependencies"
    description:
      zh: >
          零依赖任务：只装 [dev]，断言 hnswlib、fusepy、numpy 都不可导入，然后跑整套用例。
      en: >
          Zero-dependency job: installs [dev] only, asserts hnswlib, fusepy and numpy are absent, then runs the suite.
---
