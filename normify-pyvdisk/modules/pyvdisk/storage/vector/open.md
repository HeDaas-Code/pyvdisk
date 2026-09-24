---
uid: a0000601
id: pyvdisk.storage.vector.open
parent: pyvdisk.storage.vector
name: {zh: "向量盘打开", en: "Vector Disk Open"}
description:
  zh: >
      VectorDisk 生命周期，以及后续操作共用的 JSON 辅助与集合路径键化。
      
  en: >
      VectorDisk lifecycle plus the JSON helpers and collection-path keying used by every later operation.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.309Z"
fingerprint: f3bc6b45a520369279ba039c4bf06fb0bfce7e84df609d7d20d81ad24a85dc35
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
