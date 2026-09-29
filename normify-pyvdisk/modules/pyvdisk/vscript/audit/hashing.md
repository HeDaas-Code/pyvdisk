---
uid: a0000b0d
id: pyvdisk.vscript.audit.hashing
parent: pyvdisk.vscript.audit
name: {zh: "审计哈希", en: "Audit Hashing"}
description:
  zh: >
      脚本与策略的确定性哈希，以及审计哈希链：每行都带上前驱哈希，verify 报告第一条不匹配的记录——包括在真实日志段内做的手脚。
      
  en: >
      Deterministic hashing for scripts and policies, plus the audit hash chain: rows are stamped with their predecessor's hash, and verify reports the first record that does not match, including an edit made inside a real log segment.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.258Z"
fingerprint: e7c398721e85cdb58382b2b377443a1448877191f1be8c698b03443173fc2e4f
source:
  - path: "pyvdisk/vscript/audit.py"
    line: 16
    end_line: 37
apis:
  - protocol: rpc
    path: "pyvdisk.vscript.audit.script_hash"
    description:
      zh: >
          脚本的确定性哈希。
          
      en: >
          Deterministic hash of a script.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.policy_hash"
    description:
      zh: >
          策略的确定性哈希。
          
      en: >
          Deterministic hash of a policy.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.row_hash"
    description:
      zh: >
          把一条审计行与其前驱一起哈希。
          
      en: >
          Hashes one audit row together with its predecessor.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.stamp_row"
    description:
      zh: >
          为一行打上哈希链的链接字段。
          
      en: >
          Stamps a row with the hash chain link.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.chain_rows"
    description:
      zh: >
          对一批行重算整条链。
          
      en: >
          Recomputes the chain across a list of rows.
          
  - protocol: rpc
    path: "pyvdisk.vscript.audit.verify_chain"
    description:
      zh: >
          校验一条链，断开时报告断裂位置。
          
      en: >
          Verifies a chain and reports where it broke, if it did.
          
---
