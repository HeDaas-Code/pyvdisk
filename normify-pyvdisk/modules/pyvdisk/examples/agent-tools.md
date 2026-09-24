---
uid: a000033d
id: pyvdisk.examples.agent-tools
parent: pyvdisk.examples
tags: [agent, example]
name: {zh: "Agent 对接示例", en: "Agent Loop Demo"}
description:
  zh: >
      带脚本化"模型"的完整 agent loop，因此不需要 API key 与网络，可以进 CI。循环本身与对接真实客户端时完全一致，只替掉 scripted_model。示例里包含一次越权读取被拒，说明拒绝会像普通工具结果一样回灌。
  en: >
      A complete agent loop with a scripted model, so it needs no API key and no network and can run in CI. The loop is the one you would write against a real client; only scripted_model is replaced. It includes a refused out-of-root read, showing a denial flows back like any other tool result.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 021820b569bcab563e878c2d7331874621e55ca5641bac090f379fbf54f5efc1
source:
  - path: "examples/agent_tools.py"
apis:
  - protocol: file
    path: "examples/agent_tools.py:scripted_model"
    description:
      zh: >
          聊天补全调用的替身：返回下一条预置的工具调用，"模型"不再调用工具时返回 None。
      en: >
          A stand-in for a chat completion call: returns the next scripted tool call, or None when the model would stop.
---
