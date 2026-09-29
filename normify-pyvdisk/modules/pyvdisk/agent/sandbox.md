---
uid: a0000336
id: pyvdisk.agent.sandbox
parent: pyvdisk.agent
name: {zh: "沙箱门面", en: "Sandbox Facade"}
description:
  zh: >
      门面本体：create/open、Python 动词（write/read/list/make_directory/delete/exists）、脚本入口，以及 close/上下文管理器生命周期。read_only 由 capability 层强制，而不只是把工具藏起来，所以直接调用动词同样被拒。
  en: >
      The facade itself: create/open, the Python verbs (write/read/list/make_directory/delete/exists), the script entry, and the close/context-manager lifecycle. read_only is enforced by the capability layer rather than by hiding tools, so a direct verb is refused too.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 16f85eddeab0b3086fcfd918528a3d307ffcfbfa3cf7f030223ac20f360a198d
source:
  - path: "pyvdisk/sandbox.py"
    line: 316
    end_line: 474
apis:
  - protocol: rpc
    path: "sandbox:AgentSandbox.write"
    description:
      zh: >
          写入文本或字节，沿途自动建父目录。拒绝容器内部目录，也拒绝任何会越出根目录的路径。
      en: >
          Write text or bytes, creating parent directories on the way. Refuses hidden bookkeeping paths and anything that would escape the root.
  - protocol: rpc
    path: "sandbox:AgentSandbox.read"
    description:
      zh: >
          读取原始字节；read_text() 返回解码后的字符串。
      en: >
          Read raw bytes, then read_text() for a decoded string.
  - protocol: rpc
    path: "sandbox:AgentSandbox.list"
    description:
      zh: >
          列出条目及其类型与大小。容器内部路径会被过滤，模型不会看到一个用不了的名字。
      en: >
          List entries with type and size. Hidden container paths are filtered out, so the agent never sees a name it cannot use.
  - protocol: rpc
    path: "sandbox:AgentSandbox.make_directory"
    description:
      zh: >
          创建目录，自动建父级。
      en: >
          Make a directory, creating parents.
  - protocol: rpc
    path: "sandbox:AgentSandbox.delete"
    description:
      zh: >
          删除文件；recursive 为真时删整棵目录树。
      en: >
          Delete a file, or a directory tree when recursive is set.
  - protocol: rpc
    path: "sandbox:AgentSandbox.exists"
    description:
      zh: >
          可见路径是否存在。内部路径一律返回 False。
      en: >
          Whether a visible path exists. Hidden paths always answer False.
  - protocol: rpc
    path: "sandbox:AgentSandbox.create"
    description:
      zh: >
          新建或打开沙箱背后的镜像，可传 read_only、allow_delete、宿主根目录与审计上限等选项。
      en: >
          Open or create the image behind the sandbox, with options such as read_only, allow_delete, host roots and audit limits.
  - protocol: rpc
    path: "sandbox:AgentSandbox.open"
    description:
      zh: >
          重新打开已有镜像；工作区与审计记录都保留。
      en: >
          Reopen an existing image; the workspace and the audit trail both survive.
---
