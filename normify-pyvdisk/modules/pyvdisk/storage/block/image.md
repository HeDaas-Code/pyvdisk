---
uid: a0000204
id: pyvdisk.storage.block.image
parent: pyvdisk.storage.block
name: {zh: "镜像生命周期", en: "Image Lifecycle"}
description:
  zh: >
      VirtualDisk 生命周期：稀疏创建、加锁打开、上下文管理、刷新与关闭。
  en: >
      VirtualDisk lifecycle: sparse creation, locked open, context manager, flush and close.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: f3dafc0720e696593d7bf2d99ff7d99856081e9e0c20a734b75f83098f1cfb80
source:
  - path: "pyvdisk/disk.py"
    line: 60
    end_line: 141
apis:
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk"
    description:
      zh: >
          以普通宿主文件为背衬的块设备。
      en: >
          Block device backed by a plain host file.
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#create"
    description:
      zh: >
          创建指定大小的稀疏镜像文件并返回块数。
      en: >
          Create the sparse image file of a given size and return its block count.
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#open"
    description:
      zh: >
          打开镜像，写模式下获取 POSIX 写锁。
      en: >
          Open the image with optional POSIX write lock acquisition.
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#flush"
    description:
      zh: >
          刷新并 fsync 镜像文件。
      en: >
          Flush and fsync the image file.
  - protocol: rpc
    path: "pyvdisk.disk.VirtualDisk#close"
    description:
      zh: >
          释放 advisory 锁并关闭镜像。
      en: >
          Release the advisory lock and close the image.
---
