---
uid: a0000a0b
id: pyvdisk.vscript.triggers.registry
parent: pyvdisk.vscript.triggers
name: {zh: "触发器注册表", en: "Trigger Registry"}
description:
  zh: >
      触发器的注册与列举。注册即校验输入（空文件 pattern 以前能注册成功、随后把轮询循环打挂），水位线比较改用单调事件序号，而不再拿随机 uuid 作文本比较。
      
  en: >
      Trigger registration and listing. Registration validates its inputs immediately -- an empty file pattern used to register fine and then break the poll loop -- and the watermark comparison uses the monotonic event sequence instead of a random uuid compared as text.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.266Z"
fingerprint: 531549cadc018163544e7928ca49da1cef4f71bd76c32347aeb01fadee9d949f
source:
  - path: "pyvdisk/vscript/triggers.py"
    line: 14
    end_line: 73
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.Trigger"
    description:
      zh: >
          一个已注册触发器：文件 glob 或日志流，加上其动作。
          
      en: >
          One registered trigger: a file pattern or a log stream, plus its action.
          
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.TriggerRegistry"
    description:
      zh: >
          注册与列举触发器；空 pattern 或 stream 在注册处就被拒绝。
          
      en: >
          Registers and lists triggers, rejecting an empty pattern or stream up front.
          
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.event_position"
    description:
      zh: >
          事件的单调位置，优先使用序号。
          
      en: >
          Monotonic position of an event, preferring its sequence number.
          
  - protocol: rpc
    path: "pyvdisk.vscript.triggers.is_newer"
    description:
      zh: >
          判断位置是否新于水位线（两者可解析为数字时按数字比）。
          
      en: >
          Whether a position is newer than a watermark (numeric when both parse).
          
---
