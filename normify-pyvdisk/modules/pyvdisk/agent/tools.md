---
uid: a0000338
id: pyvdisk.agent.tools
parent: pyvdisk.agent
name: {zh: "工具面", en: "Tool Surface"}
description:
  zh: >
      六个内置工具：write_file、read_file、list_files、make_directory、delete_file、run_script，以及面向各框架约定的 schema 渲染，和在真正碰磁盘之前先校验参数的分发。
  en: >
      The six built-in tools: write_file, read_file, list_files, make_directory, delete_file and run_script, plus the schema rendering for each framework convention and the dispatch that validates arguments before anything touches the disk.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 16f85eddeab0b3086fcfd918528a3d307ffcfbfa3cf7f030223ac20f360a198d
source:
  - path: "pyvdisk/sandbox.py"
    line: 198
    end_line: 314
  - path: "pyvdisk/sandbox.py"
    line: 512
    end_line: 583
apis:
  - protocol: rpc
    path: "sandbox:AgentSandbox.tools"
    description:
      zh: >
          交给模型的工具定义。openai 与 anthropic 共用 {name, description, parameters}；mcp 把 schema 键换成 inputSchema。
      en: >
          The tool definitions to hand the model. openai and anthropic share {name, description, parameters}; mcp renames the schema key to inputSchema.
  - protocol: rpc
    path: "sandbox:AgentSandbox.dispatch"
    description:
      zh: >
          执行工具并始终返回字符串——拒绝也是字符串，因此可以原样回灌消息列表。
      en: >
          Run a named tool and always return a string -- a refusal is a string too, so it goes back into the message list unchanged.
  - protocol: rpc
    path: "sandbox:AgentSandbox.call"
    description:
      zh: >
          dispatch 的结构化形式：ok、content、tool、error，供需要分支判断的调用方使用。
      en: >
          The structured form of dispatch: ok, content, tool and error, for callers that branch on the outcome.
  - protocol: rpc
    path: "sandbox:TOOLS"
    description:
      zh: >
          六个内置的文件系统与脚本工具及其 JSON Schema 参数。
      en: >
          The six built-in filesystem and script tools, with their JSON Schema parameters.
---
