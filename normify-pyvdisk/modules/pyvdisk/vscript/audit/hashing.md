---
uid: a0000b0d
id: pyvdisk.vscript.audit.hashing
parent: pyvdisk.vscript.audit
name: {zh: "审计哈希", en: "Audit Hashing"}
description:
  zh: >
      脚本与策略的确定性哈希，使审计记录可跨运行与跨机器关联。
  en: >
      Deterministic hashing of scripts and policies so audit records can be correlated across runs and machines.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: e6e0c4f6567b6878156a09474961840eaaf3271a6f54be1751ac87c88fbbcebc
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 16
    end_line: 37
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.script_hash"
    description:
      zh: >
          用于关联审计记录的脚本源码稳定哈希。
      en: >
          Stable content hash of a script source used to correlate audit records.
  - protocol: rpc
    path: "pyvdisk.vscript.audit.policy_hash"
    description:
      zh: >
          单次运行实际生效策略的稳定哈希。
      en: >
          Stable hash of the effective policy for a run.
---
