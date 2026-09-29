---
uid: a0000e04
id: pyvdisk.tests.vscript-host
parent: pyvdisk.tests
name: {zh: "宿主隔离用例", en: "Host Confinement Tests"}
description:
  zh: >
      验证 host 模块拒绝根外路径——VScript 所依赖的安全边界。
      
  en: >
      Verifies the host module rejects out-of-root paths - the security boundary VScript depends on.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.253Z"
fingerprint: b0bfafaaf016b380762f3021f7ac6f169323bdcdfde4494aa05db3ab2841279b
source:
  - path: "tests/test_vscript_host.py"
apis:
  - protocol: rpc
    path: "tests/test_vscript_host.py"
    description:
      zh: >
          宿主读写根隔离断言。
          
      en: >
          Host read/write root confinement assertions.
          
deps:
  - kind: call
    to: pyvdisk.vscript.host.guard
    to_api: "rpc:pyvdisk.vscript.host.HostProxy#_check"
    label: {zh: "验证隔离", en: "verifies confinement"}
---
