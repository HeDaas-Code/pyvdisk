---
uid: a000050b
id: pyvdisk.storage.vfs.hostio
parent: pyvdisk.storage.vfs
name: {zh: "宿主交换", en: "Host Interchange"}
description:
  zh: >
      宿主交换：文件对象打开，以及虚拟与宿主文件系统之间的单文件与递归导入导出。
  en: >
      Host interchange: file object opening plus single-file and recursive import/export between the virtual and host filesystems.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 408
    end_line: 435
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#open"
    description:
      zh: >
          以模式字符串打开文件对象。
      en: >
          Open a file object with a mode string.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#import_host_file"
    description:
      zh: >
          把一个宿主文件复制进 VFS。
      en: >
          Copy one host file into the VFS.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#export_to_host"
    description:
      zh: >
          把一个 VFS 文件复制到宿主路径。
      en: >
          Copy one VFS file out to a host path.
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#import_host_tree"
    description:
      zh: >
          递归导入宿主目录树。
      en: >
          Recursively import a host directory tree.
---
