---
uid: a000070b
id: pyvdisk.storage.driver.manager
parent: pyvdisk.storage.driver
name: {zh: "磁盘管理器", en: "Disk Manager"}
description:
  zh: >
      驱动器扫描与组装：识别宿主目录中的介质及其成员如何聚合成卷。
      
  en: >
      Drive bay scanning and assembly: identify what is in a host directory and how members group into volumes.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.230Z"
fingerprint: 76f9a54ec25f379e05c35c2a7114db125da395fe4814209b88907793e6514122
source:
  - path: "pyvdisk/driver.py"
    line: 102
    end_line: 178
apis:
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager"
    description:
      zh: >
          面向单个宿主目录的驱动器。
          
      en: >
          Drive bay over one host directory.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#__init__"
    description:
      zh: >
          把管理器绑定到宿主目录与块大小。
          
      en: >
          Bind the manager to a host directory and block size.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#scan"
    description:
      zh: >
          扫描目录并探测每个 .vdisk 文件。
          
      en: >
          Scan the directory and probe every .vdisk file.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#assemble"
    description:
      zh: >
          把扫描到的盘分组为单盘、向量盘、日志盘与卷。
          
      en: >
          Group scanned disks into singles, vectors, logs and volumes.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#_unique_label"
    description:
      zh: >
          用计数器后缀解决卷标冲突。
          
      en: >
          Resolve label collisions by suffixing a counter.
          
deps:
  - kind: call
    to: pyvdisk.storage.identity.probe
    from_api: "rpc:pyvdisk.driver.DiskManager#scan"
    to_api: "rpc:pyvdisk.identity.probe_disk"
    label: {zh: "探测盘", en: "probes disks"}
---
