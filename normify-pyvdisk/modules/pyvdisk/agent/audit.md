---
uid: a000033a
id: pyvdisk.agent.audit
parent: pyvdisk.agent
name: {zh: "工具调用审计", en: "Tool Call Audit"}
description:
  zh: >
      每次调用——包括每次被拒的调用——都写入哈希链流 agent-audit，记录工具名、参数、状态、错误类型与能力摘要。"模型是不是读了不该读的路径"这个问题，事后可以从日志里回答。
  en: >
      Every call -- including every refusal -- is written to the hash-chained stream agent-audit with its tool name, arguments, status, error type and capability summary. An agent that read a path it should not have is a question the log can answer after the fact.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:40:00Z"
fingerprint: 16f85eddeab0b3086fcfd918528a3d307ffcfbfa3cf7f030223ac20f360a198d
source:
  - path: "pyvdisk/sandbox.py"
    line: 584
    end_line: 665
apis:
  - protocol: rpc
    path: "sandbox:AgentSandbox.audit"
    description:
      zh: >
          审计行，由旧到新。过滤条件为 sink 自身支持的若干项，外加 tool——它按行里记录的工具名筛选。
      en: >
          Audit rows, oldest first. Filters are the sink's own plus tool, which selects on the tool name recorded in the row.
  - protocol: rpc
    path: "sandbox:AgentSandbox.verify_audit"
    description:
      zh: >
          校验整条哈希链；在 sink 之外追加的行会把它断开。
      en: >
          Check the hash chain end to end; a row appended outside the sink breaks it.
  - protocol: rpc
    path: "sandbox:AgentSandbox.retain_audit"
    description:
      zh: >
          按流上的保留策略裁剪，同时保持哈希链仍可校验。
      en: >
          Apply the stream's retention policy while keeping the chain verifiable.
  - protocol: rpc
    path: "sandbox:AgentSandbox.stats"
    description:
      zh: >
          调用与失败计数、工具集与磁盘占用，可序列化为 JSON 进日志。
      en: >
          Call and failure counters, the tool set and disk usage, JSON-serialisable for logs.
---
