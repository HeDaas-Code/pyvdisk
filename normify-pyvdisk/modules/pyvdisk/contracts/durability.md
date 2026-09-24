---
uid: a000010e
id: pyvdisk.contracts.durability
parent: pyvdisk.contracts
name: {zh: "持久性", en: "Durability"}
description:
  zh: >
      持久性请求词表：后端可以提供强于请求的保证。
  en: >
      Durability request vocabulary: a backend may provide a stronger guarantee than requested.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 7094a1dd45da0c9a7ac8d898a6f97d47ae87d10d3f32818f4e2dfa6c7b5eab40
source:
  - path: "pyvdisk/contracts.py"
    line: 40
    end_line: 57
apis:
  - protocol: rpc
    path: "pyvdisk.contracts.DurabilityMode"
    description:
      zh: >
          持久性级别枚举：memory、flushed、synced、replicated。
      en: >
          Durability level enum: memory, flushed, synced, replicated.
  - protocol: rpc
    path: "pyvdisk.contracts.Durability"
    description:
      zh: >
          带副本数的持久性请求及其校验。
      en: >
          Requested durability with a replica count and validation.
---
