---
uid: a000050f
id: pyvdisk.storage.vfs.vfile-io
parent: pyvdisk.storage.vfs
name: {zh: "VFile 读写", en: "VFile IO"}
description:
  zh: >
      打开 VFile 上的定位读写、seek、tell、truncate、flush 与 close。
      
  en: >
      Positioned read/write, seek, tell, truncate, flush and close on an open VFile.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 550
    end_line: 598
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#read"
    description:
      zh: >
          在当前位置最多读取 size 字节。
          
      en: >
          Read up to size bytes at the current position.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#readall"
    description:
      zh: >
          读取剩余文件内容。
          
      en: >
          Read the remaining file contents.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#write"
    description:
      zh: >
          在当前位置写入字节并前移位置。
          
      en: >
          Write bytes at the current position and advance it.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#seek"
    description:
      zh: >
          移动文件位置。
          
      en: >
          Move the file position.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#tell"
    description:
      zh: >
          报告当前文件位置。
          
      en: >
          Report the current file position.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#truncate"
    description:
      zh: >
          把文件截断到指定尺寸，缺省为当前位置。
          
      en: >
          Truncate the file to a size, defaulting to the current position.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#flush"
    description:
      zh: >
          把未决写入刷新到磁盘。
          
      en: >
          Flush pending writes to the disk.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFile#close"
    description:
      zh: >
          刷新并释放文件对象。
          
      en: >
          Flush and release the file object.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.readwrite
    from_api: "rpc:pyvdisk.vfs.VFile#write"
    to_api: "rpc:pyvdisk.fs.FS#write_file"
    label: {zh: "定位写入", en: "positioned write"}
---
