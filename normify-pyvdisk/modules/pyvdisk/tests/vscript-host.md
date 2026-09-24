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
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: 4dc34e1600c660923f1dcb058df3edf5c50503760686bef5e842ccea2a101b8b
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
