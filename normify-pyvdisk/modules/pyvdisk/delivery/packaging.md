---
uid: a0000109
id: pyvdisk.delivery.packaging
parent: pyvdisk.delivery
name: {zh: "打包元数据", en: "Packaging Metadata"}
description:
  zh: >
      分发元数据：以 hnswlib 为依赖、fuse 与 dev extras、py.typed 标记，以及把 LICENSE 与 CHANGELOG.md 一并打包的 sdist 清单。
      
  en: >
      Distribution metadata: cffi-free dependency set with hnswlib, the fuse and dev extras, the py.typed marker, and the sdist manifest that ships LICENSE plus CHANGELOG.md.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.216Z"
fingerprint: eef1180eeb651e5a6edbef6a63bd38eb0f2e3244b7c927f12a61c503b23ac266
source:
  - path: "pyproject.toml"
    line: 1
  - path: "MANIFEST.in"
    line: 1
apis:
  - protocol: file
    path: "pyproject.toml"
    description:
      zh: >
          打包元数据：包名、版本、依赖、extras 与 pytest 配置。
          
      en: >
          Packaging metadata: name, version, dependencies, extras and the pytest configuration.
          
  - protocol: file
    path: "pyvdisk/py.typed"
    description:
      zh: >
          PEP 561 类型标记，使类型检查器认可本包有类型。
          
      en: >
          PEP 561 marker so type checkers see the package as typed.
          
  - protocol: file
    path: "MANIFEST.in"
    description:
      zh: >
          sdist 清单：把 LICENSE 与 CHANGELOG.md 一并打包，setuptools 不会自动带上它们。
          
      en: >
          sdist manifest: ships LICENSE and CHANGELOG.md, which setuptools does not include by itself.
          
---
