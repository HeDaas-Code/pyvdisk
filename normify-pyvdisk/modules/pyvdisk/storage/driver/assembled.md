---
uid: a0000709
id: pyvdisk.storage.driver.assembled
parent: pyvdisk.storage.driver
name: {zh: "卷组装", en: "Volume Assembly"}
description:
  zh: >
      单个卷的组装结果：找到哪些成员以及必须按何顺序打开。
  en: >
      Assembly result for one volume: which members were found and in what order they must be opened.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 29228013658c79f303b330f0476ea4155fd786b36aff9fc17e484203dc8a9edc
source:
  - path: "pyvdisk/driver.py"
    line: 30
    end_line: 54
apis:
  - protocol: rpc
    path: "pyvdisk.driver.AssembledVolume"
    description:
      zh: >
          根据共享卷元数据聚合为单个卷的成员盘集合。
      en: >
          Member disks grouped into one volume by their shared volume metadata.
  - protocol: rpc
    path: "pyvdisk.driver.AssembledVolume#complete"
    description:
      zh: >
          所有需要的成员都找到时为真。
      en: >
          True when every required member was found.
  - protocol: rpc
    path: "pyvdisk.driver.AssembledVolume#found"
    description:
      zh: >
          在宿主上找到的成员数。
      en: >
          Number of members located on the host.
  - protocol: rpc
    path: "pyvdisk.driver.AssembledVolume#needed"
    description:
      zh: >
          该卷需要的成员数。
      en: >
          Number of members the volume requires.
  - protocol: rpc
    path: "pyvdisk.driver.AssembledVolume#ordered_paths"
    description:
      zh: >
          按逻辑序号排列的成员路径。
      en: >
          Member paths in logical index order.
---
