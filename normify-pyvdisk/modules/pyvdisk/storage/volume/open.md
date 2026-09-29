---
uid: a0000703
id: pyvdisk.storage.volume.open
parent: pyvdisk.storage.volume
name: {zh: "卷打开", en: "Volume Open"}
description:
  zh: >
      卷打开路径：成员打开、跨成员一致性校验与关闭/刷新生命周期。
      
  en: >
      Volume open path: member opening, cross-member consistency verification and close/flush lifecycle.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.424Z"
fingerprint: 012cb5deb104e9e9e4018756e48a6e666fe02353c225133d0615315a17b7d08e
source:
  - path: "pyvdisk/volume.py"
    line: 180
    end_line: 259
apis:
  - protocol: rpc
    path: "pyvdisk.volume.Volume#open"
    description:
      zh: >
          打开全部成员、校验身份一致性并从 block 0 加载描述符。
          
      en: >
          Open every member, validate identity consistency and load the descriptor from block 0.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#_verify_members"
    description:
      zh: >
          校验全部预期成员已就位、可读且彼此一致。
          
      en: >
          Guard that all expected members are present, readable and mutually consistent.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#close"
    description:
      zh: >
          关闭全部成员盘。
          
      en: >
          Close every member disk.
          
  - protocol: rpc
    path: "pyvdisk.volume.Volume#flush"
    description:
      zh: >
          刷新全部成员盘。
          
      en: >
          Flush every member disk.
          
deps:
  - kind: call
    to: pyvdisk.storage.block.image
    from_api: "rpc:pyvdisk.volume.Volume#open"
    to_api: "rpc:pyvdisk.disk.VirtualDisk#open"
    label: {zh: "打开成员", en: "opens members"}
---
