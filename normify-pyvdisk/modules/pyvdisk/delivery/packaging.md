---
uid: a0000109
id: pyvdisk.delivery.packaging
parent: pyvdisk.delivery
name: {zh: "打包元数据", en: "Packaging Metadata"}
description:
  zh: >
      分发元数据：运行时依赖为空，hnswlib 与 fusepy 下沉到 vector、fuse 两个 extra，外加 py.typed 标记，以及把 LICENSE 与 CHANGELOG.md 一并打包的 sdist 清单。
  en: >
      Distribution metadata: no runtime dependencies at all, with hnswlib and fusepy moved to the vector and fuse extras, the py.typed marker, and the sdist manifest that ships LICENSE plus CHANGELOG.md.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: e83415f6936531ac1130878c36a08b49e1795946d20ecc3bf95a507560e0a608
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
