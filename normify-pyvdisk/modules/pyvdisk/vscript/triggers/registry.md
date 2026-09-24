---
uid: a0000a0b
id: pyvdisk.vscript.triggers.registry
parent: pyvdisk.vscript.triggers
name: {zh: "触发器注册表", en: "Trigger Registry"}
description:
  zh: >
      触发器声明及其持久注册表，是调度器轮询的依据。
  en: >
      Trigger declarations and their durable registry, the source of what the scheduler polls for.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: a148d13da73ae3dc4b768027bf6471b7ea1ec03669826741f4a3bf79cc35ba91
source:
  - path: "pyvdisk/vscript/triggers.py"
    line: 14
    end_line: 44
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.Trigger"
    description:
      zh: >
          一条已注册触发器：名称、类型、模式或流及级别过滤。
      en: >
          One registered trigger: name, kind, pattern or stream and level filters.
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.TriggerRegistry"
    description:
      zh: >
          以 JSON 文件为背衬的触发器注册表。
      en: >
          JSON-file-backed registry of declared triggers.
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.TriggerRegistry#save"
    description:
      zh: >
          持久化触发器映射。
      en: >
          Persist the trigger map.
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.TriggerRegistry#register"
    description:
      zh: >
          注册触发器，同名时替换。
      en: >
          Register a trigger, replacing any trigger of the same name.
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.TriggerRegistry#register_file"
    description:
      zh: >
          注册文件系统模式触发器。
      en: >
          Register a filesystem-pattern trigger.
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.TriggerRegistry#register_log"
    description:
      zh: >
          注册带级别与 logger 过滤的日志流触发器。
      en: >
          Register a log-stream trigger with level and logger filters.
---
