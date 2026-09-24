---
uid: a0000204
id: pyvdisk.storage.block.image
parent: pyvdisk.storage.block
name: {zh: "镜像生命周期", en: "Image Lifecycle"}
description:
  zh: >
      VirtualDisk 生命周期：稀疏创建、加锁打开、上下文管理、刷新与关闭。锁来自平台适配层，因此写串行化在 POSIX 与 Windows 上都真实存在，而不是悄悄退化为空操作。
  en: >
      VirtualDisk lifecycle: sparse creation, locked open, context manager, flush and close. The lock is taken from the platform layer, so write serialisation exists on both POSIX and Windows instead of silently degrading to a no-op.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: 88da0b2f3ce22b186edf88eab3d800c8e50671236a9ed1b9dbed478ff6837d16
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
          打开镜像，写锁经由平台适配层获取：POSIX 用 flock，Windows 用 msvcrt 字节区间锁。抢锁失败会关掉句柄报错，而不是无声地无锁继续跑。
      en: >
          Open the image, taking the write lock through the platform layer: flock on POSIX, an msvcrt byte range on Windows. A lock failure closes the handle and raises rather than silently continuing unlocked.
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
deps:
  - kind: call
    to: pyvdisk.platform.locking
    from_api: "rpc:pyvdisk.disk.VirtualDisk#open"
    label: {zh: "整文件写锁", en: "whole-file write lock"}
---
