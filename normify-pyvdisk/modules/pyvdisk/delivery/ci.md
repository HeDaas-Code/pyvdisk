---
uid: a000010a
id: pyvdisk.delivery.ci
parent: pyvdisk.delivery
name: {zh: "测试工作流", en: "Test Workflow"}
description:
  zh: >
      CI 工作流：在 push 与 pull request 上安装 dev extras 并在 3.9–3.12 矩阵上运行 pytest，使声明的 requires-python 下限由最老的矩阵任务强制，而不是靠假设。
      
  en: >
      CI workflow: installs the dev extras and runs the pytest suite on push and pull request across the 3.9-3.12 matrix, so the declared requires-python floor is enforced by the oldest job rather than assumed.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.215Z"
fingerprint: b1583a09123f8c3ad3d2e52ae4bc88ff01e6db7a88c3336853b06482634e20eb
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
