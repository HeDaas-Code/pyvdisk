---
uid: a0000333
id: pyvdisk.platform.durability
parent: pyvdisk.platform
name: {zh: "持久化与身份", en: "Durability and Identity"}
description:
  zh: >
      其余平台差异：改名后刷盘目录、报告进程身份、探测符号链接支持、选择当前实现。它们都返回可判断的值而非抛异常，因为单拿出来都不致命。
      
  en: >
      The remaining platform differences: flushing a directory after a rename, reporting process identity, probing symlink support, and selecting the implementation in force. Each returns a value the caller can branch on instead of raising, because none of them is fatal on its own.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T11:40:47.981Z"
fingerprint: 079a5edb2e3962afd8293877a634189cbdef72a96e9d5881983523ef5a531fb1
source:
  - path: "pyvdisk/compat.py"
    line: 202
    end_line: 283
  - path: "pyvdisk/compat.py"
    line: 41
    end_line: 100
apis:
  - protocol: rpc
    path: "pyvdisk.compat.fsync_dir"
    description:
      zh: >
          刷盘目录，让改名能抵住崩溃。真的执行了才返回 True；Windows 无法把目录当文件打开，所以返回 False 表示"未执行"，而不是假装成功。
      en: >
          Flush a directory so a rename survives a crash. Returns True when it actually ran; Windows cannot open a directory as a file, so it returns False to mean not performed rather than claiming success.
  - protocol: rpc
    path: "pyvdisk.compat.uid"
    description:
      zh: >
          进程 uid；平台没有该概念时返回 0。
      en: >
          Effective uid, or 0 where the platform has no such notion.
  - protocol: rpc
    path: "pyvdisk.compat.gid"
    description:
      zh: >
          进程 gid；平台没有该概念时返回 0。
      en: >
          Effective gid, or 0 where the platform has no such notion.
  - protocol: rpc
    path: "pyvdisk.compat.uid_or"
    description:
      zh: >
          取 uid，无该概念时用传入的缺省值。用它而不是 `uid() or default`：uid 0 是 root，不是"未设置"。
      en: >
          uid, or the given fallback. Prefer this over `uid() or default`: uid 0 is root, not unset.
  - protocol: rpc
    path: "pyvdisk.compat.gid_or"
    description:
      zh: >
          取 gid，无该概念时用传入的缺省值。
      en: >
          gid, or the given fallback.
  - protocol: rpc
    path: "pyvdisk.compat.can_symlink"
    description:
      zh: >
          探测指定目录下能否创建符号链接（不抛异常）。Windows 需要开发者模式，调用方据此降级而不是直接失败。
      en: >
          Probe whether a symlink can be created in the given directory without raising. Windows needs developer mode, so callers degrade instead of failing.
---
