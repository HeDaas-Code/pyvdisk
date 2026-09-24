---
uid: a0000711
id: pyvdisk.storage.fuse.mount
parent: pyvdisk.storage.fuse
name: {zh: "FUSE 挂载入口", en: "FUSE Mount Entry"}
description:
  zh: >
      公开挂载入口，包含容忍忙挂载的 main 循环补丁与线程化变体。
      
  en: >
      Public mount entry points, including the patched main loop that tolerates busy mounts and the threaded variant.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 5fe2c5a2cde43ccd63a7a2c90ca4f237f91e4c1de74900e83ebc49d9e6dc5193
source:
  - path: "pyvdisk/fuse_mount.py"
    line: 234
    end_line: 283
apis:
  - protocol: rpc
    path: "pyvdisk.fuse_mount.mount"
    description:
      zh: >
          把 VFS 挂载到宿主挂载点；缺少 fusepy 时给出清晰错误。
          
      en: >
          Mount a VFS at a host mountpoint, raising a clear error when fusepy is unavailable.
          
  - protocol: rpc
    path: "pyvdisk.fuse_mount.mount_in_thread"
    description:
      zh: >
          在后台线程运行 FUSE 主循环。
          
      en: >
          Run the FUSE main loop on a background thread.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.lifetime
    from_api: "rpc:pyvdisk.fuse_mount.mount"
    to_api: "rpc:pyvdisk.vfs.VFS#mount"
    label: {zh: "挂载 VFS", en: "mounts VFS"}
---
