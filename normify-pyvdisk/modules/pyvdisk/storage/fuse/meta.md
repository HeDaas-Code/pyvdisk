---
uid: a000070e
id: pyvdisk.storage.fuse.meta
parent: pyvdisk.storage.fuse
name: {zh: "FUSE 属性", en: "FUSE Attributes"}
description:
  zh: >
      stat 到 fuse 的映射与目录项对象：类型、mode、大小、时间戳与属主。身份来自平台适配层，同时修掉一个真实缺陷：此前 uid 0（root）与"平台没有 uid"无法区分。
      
  en: >
      Stat-to-fuse mapping and the entry object: type, mode, size, timestamps and ownership. Identity comes from the platform layer, which also fixes a real bug: uid 0 (root) was previously indistinguishable from "no uid available".
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T11:37:33.368Z"
fingerprint: c711d0ed315e831e5d1d2873c7557dc5e72c8dcb01ee91556eb39cb3065c5d76
source:
  - path: "pyvdisk/fuse_mount.py"
    line: 24
    end_line: 80
apis:
  - protocol: rpc
    path: "pyvdisk.fuse_mount._have_fuse"
    description:
      zh: >
          fusepy 可导入时为真。
          
      en: >
          True when fusepy is importable.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations"
    description:
      zh: >
          把内核调用翻译为 VFS 调用的 FUSE 操作类。
          
      en: >
          FUSE operation class translating kernel calls into VFS calls.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_getattr"
    description:
      zh: >
          通过 VFS stat 实现 getattr。
          
      en: >
          Implement getattr by statting through the VFS.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount._VFuseOperations#_readdir"
    description:
      zh: >
          通过列举 VFS 目录实现 readdir。
          
      en: >
          Implement readdir by listing the VFS directory.
          
deps:
  - kind: call
    to: pyvdisk.platform.durability
    from_api: "rpc:pyvdisk.fuse_mount._VFuseOperations#_getattr"
    label: {zh: "进程身份", en: "process identity"}
---
