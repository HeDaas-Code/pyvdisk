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
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 29228013658c79f303b330f0476ea4155fd786b36aff9fc17e484203dc8a9edc
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
