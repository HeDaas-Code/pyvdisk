---
uid: a0000507
id: pyvdisk.storage.vfs.files
parent: pyvdisk.storage.vfs
name: {zh: "整文件 IO", en: "Whole-File IO"}
description:
  zh: >
      建立在定位式 FS 文件 API 之上的整文件读、写与追加便利接口。
      
  en: >
      Whole-file read, write and append conveniences on top of the positioned FS file API.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 78228a31bb30dd6ec27c3232a667df6190a704471e3002c8369ace907f2cd070
source:
  - path: "pyvdisk/vfs.py"
    line: 265
    end_line: 302
apis:
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#read_file"
    description:
      zh: >
          把整个文件读为 bytes。
          
      en: >
          Read a whole file into bytes.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#write_file"
    description:
      zh: >
          把字节写入路径并替换其内容。
          
      en: >
          Write bytes to a path, replacing its contents.
          
  - protocol: rpc
    path: "pyvdisk.vfs.VFS#append_file"
    description:
      zh: >
          向路径追加字节。
          
      en: >
          Append bytes to a path.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.readwrite
    from_api: "rpc:pyvdisk.vfs.VFS#write_file"
    to_api: "rpc:pyvdisk.fs.FS#write_path"
    label: {zh: "写入文件数据", en: "writes file data"}
---
