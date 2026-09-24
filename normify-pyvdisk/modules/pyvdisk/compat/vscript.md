---
uid: a0000f02
id: pyvdisk.compat.vscript
parent: pyvdisk.compat
tags: [compat]
name: {zh: "VScript 检查点垫片", en: "VScript Checkpoint Shim"}
description:
  zh: >
      遗留垫片：在存储移入 infrastructure 后仍保留 vscript.checkpoint 模块路径可导入。
  en: >
      Legacy shim that keeps the vscript.checkpoint module path importable after the store moved into infrastructure.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: ed01dfc21949e087c9a325e41118c960083b90243e8ab58b85a860de7cd2a8e0
source:
  - path: "pyvdisk/vscript/checkpoint.py"
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.checkpoint.CheckpointStore"
    description:
      zh: >
          为旧调用方重导出的遗留检查点导入路径。
      en: >
          Legacy checkpoint import path re-exported for older callers.
---
