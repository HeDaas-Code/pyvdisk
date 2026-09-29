---
uid: a0000207
id: pyvdisk.storage.identity.format
parent: pyvdisk.storage.identity
name: {zh: "身份格式", en: "Identity Format"}
description:
  zh: >
      尾标布局常量、.vdisk 后缀规则与身份错误类型。
  en: >
      Trailer layout constants, the .vdisk suffix rule and the identity error type.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 79d877b6840991d3a1de01a41018bf417b9d899c8649bb49dd7b7f5f9ed0f2ab
source:
  - path: "pyvdisk/identity.py"
    line: 30
    end_line: 53
apis:
  - protocol: rpc
    path: "pyvdisk.identity.validate_disk_path"
    description:
      zh: >
          要求用户可见的磁盘容器使用 .vdisk 后缀。
      en: >
          Require a .vdisk suffix for user-visible disk containers.
  - protocol: rpc
    path: "pyvdisk.identity.IdentityError"
    description:
      zh: >
          身份解析或写入失败时抛出。
      en: >
          Raised when a disk identity cannot be parsed or written.
  - protocol: rpc
    path: "pyvdisk.identity.DISK_ID_TRAILER_SIZE"
    description:
      zh: >
          block 0 末尾保留的尾标长度常量（112 字节）。
      en: >
          Trailer length constant (112 bytes) reserved at the end of block 0.
---
