---
uid: a0000a0c
id: pyvdisk.vscript.triggers.daemon
parent: pyvdisk.vscript.triggers
name: {zh: "调度守护进程", en: "Scheduler Daemon"}
description:
  zh: >
      调度守护进程：文件与日志事件检测、经检查点的精确一次去重，以及轮询循环。
      
  en: >
      The scheduling daemon: file and log event detection, exactly-once dedup through checkpoints, and the polling loop.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:22:04.609Z"
fingerprint: a148d13da73ae3dc4b768027bf6471b7ea1ec03669826741f4a3bf79cc35ba91
source:
  - path: "pyvdisk/vscript/triggers.py"
    line: 46
    end_line: 83
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.SchedulerDaemon"
    description:
      zh: >
          把文件与日志事件转为处理调用的轮询守护进程。
          
      en: >
          Polling daemon that turns file and log events into handler invocations.
          
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.SchedulerDaemon#poll_once"
    description:
      zh: >
          对每条触发器轮询一次，并经检查点存储对已发事件去重。
          
      en: >
          Poll each trigger once, deduplicating emitted events through the checkpoint store.
          
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.SchedulerDaemon#run"
    description:
      zh: >
          持续轮询直到 stop 事件被设置。
          
      en: >
          Run the polling loop until the stop event is set.
          
deps:
  - kind: call
    to: pyvdisk.storage.checkpoint.triggers
    from_api: "rpc:pyvdisk.vscript.triggers.SchedulerDaemon#poll_once"
    to_api: "rpc:pyvdisk.infrastructure.checkpoint.CheckpointStore#mark_success"
    label: {zh: "事件去重", en: "dedups events"}
  - kind: call
    to: pyvdisk.vscript.triggers.registry
    from_api: "rpc:pyvdisk.vscript.triggers.SchedulerDaemon#poll_once"
    to_api: "rpc:pyvdisk.vscript.triggers.TriggerRegistry"
    label: {zh: "读取触发器", en: "reads triggers"}
---
