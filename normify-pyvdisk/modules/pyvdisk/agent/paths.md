---
uid: a0000337
id: pyvdisk.agent.paths
parent: pyvdisk.agent
name: {zh: "路径约束", en: "Path Confinement"}
description:
  zh: >
      沙箱内"路径意味着什么"的唯一一份定义。反斜杠输入被归一化，Windows 样式的路径留在镜像内部，.. 是拒绝而不是解析，容器自身的簿记对读写与列举一律不可见。
  en: >
      The one definition of what a path means inside the sandbox: backslash input is normalised, Windows-looking paths stay inside the image, .. is refused rather than resolved, and the container's own bookkeeping is hidden from reads, writes and listings alike.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 16f85eddeab0b3086fcfd918528a3d307ffcfbfa3cf7f030223ac20f360a198d
source:
  - path: "pyvdisk/sandbox.py"
    line: 60
    end_line: 195
  - path: "pyvdisk/sandbox.py"
    line: 387
    end_line: 420
apis:
  - protocol: rpc
    path: "sandbox:AgentSandbox._normalize"
    description:
      zh: >
          把模型给的路径映射进沙箱命名空间：反斜杠归一化，C:\Windows 变成 /C:/Windows。
      en: >
          Map a model-supplied path into the sandbox namespace: backslashes are normalised and C:\Windows becomes /C:/Windows.
  - protocol: rpc
    path: "sandbox:AgentSandbox._visible"
    description:
      zh: >
          先归一化，再拒绝容器自身的簿记路径。
      en: >
          Normalise, then refuse the container's own bookkeeping paths.
  - protocol: rpc
    path: "sandbox:_hidden"
    description:
      zh: >
          路径是否属于 /.system、/.vectors、/.logs，或是根目录下的清单文件。
      en: >
          Whether a path is under /.system, /.vectors or /.logs, or is one of the root-level manifests.
---
