---
uid: a0000109
id: pyvdisk.delivery.packaging
parent: pyvdisk.delivery
name: {zh: "打包元数据", en: "Packaging Metadata"}
description:
  zh: >
      分发元数据：包名、0.3.0 版本、依赖集、可选 fuse extra 与 py.typed 标记。
  en: >
      Distribution metadata: package name, version 0.3.0, dependency set, optional fuse extra and the py.typed marker.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 3719372451f85f52b322431d54f57c051b4b16d0ecc5ad21d3f11aeae3d52827
source:
  - path: "pyproject.toml"
apis:
  - protocol: file
    path: "pyproject.toml"
    description:
      zh: >
          分发元数据：名称、版本、依赖与 extras。
      en: >
          Distribution metadata: name, version, dependencies and extras.
  - protocol: file
    path: "pyvdisk/py.typed"
    description:
      zh: >
          随包发布的 PEP 561 内联类型标记。
      en: >
          PEP 561 inline type marker published with the package.
---
