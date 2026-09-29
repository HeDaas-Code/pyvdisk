---
uid: a000032f
id: pyvdisk.platform
parent: pyvdisk
name: {zh: "平台适配层", en: "Platform Adaptation"}
description:
  zh: >
      唯一直接触碰操作系统原语的地方：定位读写、整文件锁、目录 fsync、进程身份与符号链接支持。其余模块一律经由它，平台差异只处理一次，而不是在每个调用点各写一份。
      
  en: >
      The single place that touches operating-system primitives: positional IO, whole-file locking, directory fsync, process identity and symlink support. Every other module goes through it, so Windows differences are handled once instead of at each call site.
      
revision: 3cb47877135592bd8565726610c54ebd1ecd9fba
updated_at: "2026-09-24T11:51:39.623Z"
fingerprint: a36d0bc58d4a6da6854f4c155bbc8fca838d7a7ff82d379b18b17490bdb29657
source:
  - path: "pyvdisk/compat.py"
  - path: "pyvdisk/disk.py"
  - path: "pyvdisk/infrastructure/checkpoint.py"
  - path: "pyvdisk/vscript/host.py"
  - path: "pyvdisk/fuse_mount.py"
---
