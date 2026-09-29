---
uid: a000070a
id: pyvdisk.storage.driver.mounts
parent: pyvdisk.storage.driver
name: {zh: "挂载介质", en: "Mounted Media"}
description:
  zh: >
      日志盘、向量盘与文件系统介质的统一挂载包装，使驱动器可统一处理。
      
  en: >
      Uniform mounted-object wrappers for log, vector and filesystem media so the drive manager can treat them alike.
      
revision: c3881eee5dced2b180cd3b383e5d848026224154
updated_at: "2026-09-24T09:58:38.231Z"
fingerprint: 76f9a54ec25f379e05c35c2a7114db125da395fe4814209b88907793e6514122
source:
  - path: "pyvdisk/driver.py"
    line: 56
    end_line: 100
apis:
  - protocol: rpc
    path: "pyvdisk.driver.MountedLog"
    description:
      zh: >
          已挂载的日志盘及其自动创建的默认流。
          
      en: >
          A mounted log disk together with its auto-created default stream.
          
  - protocol: rpc
    path: "pyvdisk.driver.MountedVector"
    description:
      zh: >
          已挂载的向量盘。
          
      en: >
          A mounted vector disk.
          
  - protocol: rpc
    path: "pyvdisk.driver.MountedFS"
    description:
      zh: >
          已挂载的文件系统卷及其 VFS 句柄与卷标。
          
      en: >
          A mounted filesystem volume with its VFS handle and label.
          
  - protocol: rpc
    path: "pyvdisk.driver.MountedFS#__enter__"
    description:
      zh: >
          返回已挂载的 VFS 以用作上下文管理器。
          
      en: >
          Return the mounted VFS for use as a context manager.
          
  - protocol: rpc
    path: "pyvdisk.driver.MountedFS#__exit__"
    description:
      zh: >
          上下文退出时关闭已挂载的 VFS。
          
      en: >
          Close the mounted VFS on context exit.
          
  - protocol: rpc
    path: "pyvdisk.driver.MountedLog#close"
    description:
      zh: >
          关闭已挂载对象。
          
      en: >
          Close the mounted object.
          
---
