---
uid: a0000601
id: pyvdisk.storage.vector.open
parent: pyvdisk.storage.vector
name: {zh: "向量盘打开", en: "Vector Disk Open"}
description:
  zh: >
      VectorDisk 的构建与挂载。这里不再要求装 hnswlib：集合用内置 flat 索引也能打开并作答，只有恰好装了加速器才会用它。
  en: >
      VectorDisk construction and mounting. Nothing here requires hnswlib: a collection opens and answers with the built-in flat index, and the accelerator is picked up only if it happens to be installed.
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T13:45:00Z"
fingerprint: ee801e56c4d436543de323aa02bb0c3a4e78339ef28b5c1ec180ad68cee817b0
source:
  - path: "pyvdisk/vector_disk.py"
    line: 13
    end_line: 127
apis:
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDiskError"
    description:
      zh: >
          向量盘特定失败（如缺少 hnswlib 后端）时抛出。
          
      en: >
          Raised for vector-disk specific failures such as a missing hnswlib backend.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk"
    description:
      zh: >
          以集合存储形式暴露的 .vdisk 镜像。
          
      en: >
          A .vdisk image exposed as a collection store.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#create"
    description:
      zh: >
          格式化新的向量盘镜像。
          
      en: >
          Format a new vector disk image.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#mount"
    description:
      zh: >
          挂载镜像并加载向量命名空间。
          
      en: >
          Mount the image and load the vector namespace.
          
  - protocol: rpc
    path: "pyvdisk.vector_disk.VectorDisk#close"
    description:
      zh: >
          关闭底层 VFS。
          
      en: >
          Close the underlying VFS.
          
deps:
  - kind: call
    to: pyvdisk.storage.vfs.lifetime
    from_api: "rpc:pyvdisk.vector_disk.VectorDisk#mount"
    to_api: "rpc:pyvdisk.vfs.VFS#mount"
    label: {zh: "挂载 VFS", en: "mounts VFS"}
---
