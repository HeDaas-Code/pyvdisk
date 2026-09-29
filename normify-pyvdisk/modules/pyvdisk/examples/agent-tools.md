---
uid: a000033d
id: pyvdisk.examples.agent-tools
parent: pyvdisk.examples
tags: [agent, example]
name: {zh: "Agent 对接示例", en: "Agent Loop Demo"}
description:
  zh: >
      带脚本化"模型"的完整 agent loop，形状与 README 示例完全一致，因此不需要 API key 与网络，可以进 CI。示例里包含一次越权读取被拒，以及一轮同时请求两个工具，覆盖拒绝路径与多调用列表路径。
      
  en: >
      A complete agent loop with a scripted model, shaped exactly like the README demo, so it needs no API key and no network and can run in CI. It includes a refused out-of-root read and a turn that requests two tools at once, covering both the refusal path and the multi-call list path.
      
revision: f163400c098f68cbdfb0393a9bf488037d012aaf
updated_at: "2026-09-24T11:48:38.686Z"
fingerprint: 38e6efd2ed3bfcec7954b1a00d09cc90b41ca8906175dcbb023a72fefed9f9b7
source:
  - path: "examples/agent_tools.py"
apis:
  - protocol: file
    path: "examples/agent_tools.py:scripted_model"
    description:
      zh: >
          单次聊天补全调用的替身：返回供循环消费的 assistant 消息；脚本跑完后返回 tool_calls 为空的消息。
          
      en: >
          A stand-in for one chat completion call: returns an assistant message whose tool_calls the loop consumes, and an empty tool_calls list when the script runs out.
          
---
