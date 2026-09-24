---
uid: a000060c
id: pyvdisk.storage.logging.context
parent: pyvdisk.storage.logging
name: {zh: "日志上下文", en: "Log Context"}
description:
  zh: >
      基于 contextvar 的环境字段，会合入每个产出的事件。
      
  en: >
      Contextvar-based ambient fields that are merged into every emitted event.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.236Z"
fingerprint: b09c0a892a4245c749b1b656f75fea42c069ef41438429402f0b180223f5b281
source:
  - path: "pyvdisk/logging_core.py"
    line: 51
    end_line: 59
apis:
  - protocol: rpc
    path: "pyvdisk.logging_core.log_context"
    description:
      zh: >
          向环境日志上下文添加字段的上下文管理器。
          
      en: >
          Context manager adding fields to the ambient log context.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.bind_context"
    description:
      zh: >
          把字段永久合入环境日志上下文。
          
      en: >
          Permanently merge fields into the ambient log context.
          
  - protocol: rpc
    path: "pyvdisk.logging_core.clear_context"
    description:
      zh: >
          清空环境日志上下文。
          
      en: >
          Clear the ambient log context.
          
---
