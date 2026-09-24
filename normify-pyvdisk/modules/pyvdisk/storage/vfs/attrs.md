---
uid: a000050a
id: pyvdisk.storage.vfs.attrs
parent: pyvdisk.storage.vfs
name: {zh: "元数据变更", en: "Metadata Writes"}
description:
  zh: >
      VFS 门面上的元数据变更：模式、属主、时间戳、权限检查与截断。
  en: >
      Metadata mutations on the VFS facade: mode, ownership, timestamps, access checks and truncation.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 364
    end_line: 406
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#chmod"
    description:
      zh: >
          修改模式位，可选穿透符号链接。
      en: >
          Change mode bits, optionally through a symlink.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#chown"
    description:
      zh: >
          修改属主，可选穿透符号链接。
      en: >
          Change ownership, optionally through a symlink.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#utime"
    description:
      zh: >
          设置时间戳，可选穿透符号链接。
      en: >
          Set timestamps, optionally through a symlink.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#access"
    description:
      zh: >
          对路径做权限检查。
      en: >
          Permission check on a path.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#truncate"
    description:
      zh: >
          调整路径上文件的尺寸。
      en: >
          Resize a file at a path.
---
