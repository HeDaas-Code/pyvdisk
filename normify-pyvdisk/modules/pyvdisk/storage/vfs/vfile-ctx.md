---
uid: a0000510
id: pyvdisk.storage.vfs.vfile-ctx
parent: pyvdisk.storage.vfs
name: {zh: "VFile 协议", en: "VFile Protocol"}
description:
  zh: >
      打开 VFile 对象的 with 语句与迭代协议。
  en: >
      with-statement and iteration protocol for open VFile objects.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 600
    end_line: 612
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#__enter__"
    description:
      zh: >
          上下文管理器入口，返回打开的文件对象。
      en: >
          Context manager entry returning the open file object.
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#__exit__"
    description:
      zh: >
          上下文管理器退出时关闭文件对象。
      en: >
          Context manager exit that closes the file object.
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#__iter__"
    description:
      zh: >
          按行迭代文件。
      en: >
          Iterate over the file line by line.
---
