---
uid: a000070d
id: pyvdisk.storage.driver.lifecycle
parent: pyvdisk.storage.driver
name: {zh: "卸载与热插拔", en: "Unmount and Hotplug"}
description:
  zh: >
      模拟驱动器的卸载、热插拔重扫与诊断汇总。
      
  en: >
      Unmount, hotplug rescan and diagnostic summary for the simulated drive bay.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.230Z"
fingerprint: 76f9a54ec25f379e05c35c2a7114db125da395fe4814209b88907793e6514122
source:
  - path: "pyvdisk/driver.py"
    line: 259
    end_line: 310
apis:
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#unmount"
    description:
      zh: >
          卸载单个卷标。
          
      en: >
          Unmount one label.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#unmount_all"
    description:
      zh: >
          卸载全部已挂载介质。
          
      en: >
          Unmount every mounted medium.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#hotplug"
    description:
      zh: >
          重新扫描目录并挂载新出现的盘。
          
      en: >
          Rescan the directory and mount newly appeared disks.
          
  - protocol: rpc
    path: "pyvdisk.driver.DiskManager#summary"
    description:
      zh: >
          汇总已扫描、已组装与已挂载介质以供诊断。
          
      en: >
          Summarize scanned, assembled and mounted media for diagnostics.
          
---
