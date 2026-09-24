---
uid: a0000340
id: pyvdisk.tests.no-dependency
parent: pyvdisk.tests
name: {zh: "零依赖测试", en: "Zero Dependency Tests"}
description:
  zh: >
      同一个承诺的三层校验：pyproject 不声明运行时依赖且把加速器留在 extra 里；屏蔽 hnswlib 时 VectorDisk 仍能正确作答，两种后端结果一致且能互读对方写的盘；examples/quickstart.py 在屏蔽 hnswlib 的子进程里能跑完，示例不会悄悄地开始依赖它。
  en: >
      Three layers of the same claim: pyproject declares no runtime dependencies and keeps the accelerators as extras; VectorDisk answers correctly with hnswlib blocked, and the two backends agree and read each other's files; and examples/quickstart.py runs to completion in a subprocess with hnswlib blocked, so the example cannot quietly start needing it.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: aca58c61b9b691e1849bc2f3a598cbaa1fd1e5c7db7193c969d3adbeb0c37073
source:
  - path: "tests/test_no_dependency_path.py"
apis:
  - protocol: file
    path: "tests/test_no_dependency_path.py"
    description:
      zh: >
          零依赖承诺：从打包、后端与示例三个层面校验。
      en: >
          The zero-dependency promise, checked at packaging, backend and example level.
---
