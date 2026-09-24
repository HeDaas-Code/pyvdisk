---
uid: a000070c
id: pyvdisk.storage.driver.mounting
parent: pyvdisk.storage.driver
name: {zh: "挂载分发", en: "Mount Dispatch"}
description:
  zh: >
      挂载分发：每类介质一条路径，以及 CLI 使用的整体挂载与卷标查询。
      
  en: >
      Mounting dispatch: one code path per medium kind plus the aggregate mount-all and label lookup used by the CLI.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 29228013658c79f303b330f0476ea4155fd786b36aff9fc17e484203dc8a9edc
source:
  - path: "pyvdisk/driver.py"
    line: 180
    end_line: 258
apis:
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#mount_all"
    description:
      zh: >
          挂载全部已组装介质并返回卷标到 VFS 的映射。
          
      en: >
          Mount all assembled media and return the label-to-VFS map.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#get"
    description:
      zh: >
          按卷标查询单个已挂载介质。
          
      en: >
          Look up one mounted medium by label.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#labels"
    description:
      zh: >
          列出当前已挂载介质的卷标。
          
      en: >
          List the labels of currently mounted media.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#_mount_single"
    description:
      zh: >
          挂载单盘文件系统镜像。
          
      en: >
          Mount a single-disk filesystem image.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#_mount_vector"
    description:
      zh: >
          挂载向量盘。
          
      en: >
          Mount a vector disk.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#_mount_log"
    description:
      zh: >
          挂载日志盘。
          
      en: >
          Mount a log disk.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#_mount_volume"
    description:
      zh: >
          挂载已组装的多成员卷。
          
      en: >
          Mount an assembled multi-member volume.
          
deps:
  - kind: call
    to: pyvdisk.storage.vector.open
    from_api: "rpc:pyvdisk.driver.DiskManager#_mount_vector"
    to_api: "rpc:pyvdisk.vector_disk.VectorDisk#mount"
    label: {zh: "挂载向量盘", en: "mounts vector disk"}
  - kind: call
    to: pyvdisk.storage.log.open
    from_api: "rpc:pyvdisk.driver.DiskManager#_mount_log"
    to_api: "rpc:pyvdisk.log_disk.LogDisk#mount"
    label: {zh: "挂载日志盘", en: "mounts log disk"}
  - kind: call
    to: pyvdisk.storage.volume.open
    from_api: "rpc:pyvdisk.driver.DiskManager#_mount_volume"
    to_api: "rpc:pyvdisk.volume.Volume#open"
    label: {zh: "打开卷", en: "opens volume"}
---
