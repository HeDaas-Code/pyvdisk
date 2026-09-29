---
uid: a0000a09
id: pyvdisk.vscript.mounts
parent: pyvdisk.vscript
name: {zh: "挂载注册表", en: "Mount Registry"}
description:
  zh: >
      挂载授权：把 CLI 挂载参数转为能力受限句柄并在运行后关闭的注册表。
      
  en: >
      Mount authorization: the registry that turns CLI mount flags into capability-limited handles and closes them after the run.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 585606c58ad1f62de4c8a0ae519916c27755abe335bbb128d5be7c67cd88d4c4
source:
  - path: "pyvdisk/vscript/mounts.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.mounts.MountRegistry"
    description:
      zh: >
          单次脚本运行所授予的挂载句柄注册表。
          
      en: >
          Registry of mount handles granted to one script run.
          
  - protocol: rpc
    path: "pyvdisk.vscript.mounts.MountRegistry#grant"
    description:
      zh: >
          在目标上按权限与根范围授予具名句柄。
          
      en: >
          Grant a named handle over a target with permissions and a root scope.
          
  - protocol: rpc
    path: "pyvdisk.vscript.mounts.MountRegistry#open"
    description:
      zh: >
          打开资源并为其授予句柄。
          
      en: >
          Open a resource and grant a handle for it.
          
  - protocol: rpc
    path: "pyvdisk.vscript.mounts.MountRegistry#get"
    description:
      zh: >
          按名称查询已授予能力。
          
      en: >
          Look up a granted capability by name.
          
  - protocol: rpc
    path: "pyvdisk.vscript.mounts.MountRegistry#handles"
    description:
      zh: >
          返回脚本可见的句柄映射。
          
      en: >
          Return the script-visible handle map.
          
  - protocol: rpc
    path: "pyvdisk.vscript.mounts.MountRegistry#close"
    description:
      zh: >
          运行结束时关闭全部自有资源。
          
      en: >
          Close every owned resource at the end of a run.
          
deps:
  - kind: call
    to: pyvdisk.vscript.policy.capability
    from_api: "rpc:pyvdisk.vscript.mounts.MountRegistry#grant"
    to_api: "rpc:pyvdisk.vscript.policy.Capability"
    label: {zh: "创建能力", en: "creates capability"}
---
