---
uid: a000050e
id: pyvdisk.storage.vfs.vfile
parent: pyvdisk.storage.vfs
name: {zh: "VFile 对象", en: "VFile Object"}
description:
  zh: >
      打开文件对象的 VFile 构造与 inode 自省。
  en: >
      VFile construction and inode introspection for the open-file object.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 501
    end_line: 549
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFile"
    description:
      zh: >
          VFS 路径之上的缓冲文件对象。
      en: >
          Buffered file object over a VFS path.
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#__init__"
    description:
      zh: >
          把文件对象绑定到路径并解析模式字符串。
      en: >
          Bind a file object to a path and parse its mode string.
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#ino"
    description:
      zh: >
          返回该文件对象背后的 inode 号。
      en: >
          Return the inode number behind this file object.
---
