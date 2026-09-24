---
uid: a0000339
id: pyvdisk.agent.script
parent: pyvdisk.agent
name: {zh: "盘内脚本", en: "Sandboxed Scripts"}
description:
  zh: >
      盘内 VScript 入口：脚本带着沙箱挂载运行，默认禁止宿主访问，stdout 返回给模型。挂载前面的适配器同样把容器簿记从 listdir、walk、glob 里滤掉，脚本入口不会变成规则更松的第二个入口。
  en: >
      The in-disk VScript entry: a script runs with the sandbox mounted, host access denied by default, and its stdout returned to the model. The adapter in front of the mount filters container bookkeeping out of listdir, walk and glob as well, so the script door is not a second entrance with looser rules.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 16f85eddeab0b3086fcfd918528a3d307ffcfbfa3cf7f030223ac20f360a198d
source:
  - path: "pyvdisk/sandbox.py"
    line: 72
    end_line: 195
  - path: "pyvdisk/sandbox.py"
    line: 476
    end_line: 510
apis:
  - protocol: rpc
    path: "sandbox:AgentSandbox.run"
    description:
      zh: >
          执行 VScript 程序，沙箱绑定为变量 sandbox。未配置宿主根目录时宿主访问一律被拒；墙钟时间、输出与写入字节数都有上限。
      en: >
          Run a VScript program with the sandbox bound as the variable sandbox. Host access is refused unless roots were configured; wall time, output and written bytes are all capped.
  - protocol: rpc
    path: "sandbox:_SandboxFS"
    description:
      zh: >
          脚本看到的文件系统。每个路径都走与 Python 动词相同的可见性规则，两个入口不可能出现不一致。
      en: >
          The filesystem a script sees. Every path is translated through the same visibility rule the Python verbs use, so the two entrances cannot disagree.
---
