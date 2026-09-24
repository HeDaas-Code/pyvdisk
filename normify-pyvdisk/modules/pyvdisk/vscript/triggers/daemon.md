---
uid: a0000a0c
id: pyvdisk.vscript.triggers.daemon
parent: pyvdisk.vscript.triggers
name: {zh: "调度守护进程", en: "Scheduler Daemon"}
description:
  zh: >
      轮询守护进程：每轮评估到期的文件与日志触发器并分发动作，按单调水位线排序事件，不再静默跳过到期事件。
      
  en: >
      The polling daemon: evaluates due file and log triggers once per tick and dispatches their actions, ordering events by the monotonic watermark so no due event is silently skipped.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.266Z"
fingerprint: 531549cadc018163544e7928ca49da1cef4f71bd76c32347aeb01fadee9d949f
source:
  - path: "pyvdisk/vscript/triggers.py"
    line: 75
    end_line: 108
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
