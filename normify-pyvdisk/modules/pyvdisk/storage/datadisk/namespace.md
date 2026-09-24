---
uid: a000080a
id: pyvdisk.storage.datadisk.namespace
parent: pyvdisk.storage.datadisk
name: {zh: "文件系统命名空间", en: "Filesystem Namespace"}
description:
  zh: >
      事务性文件系统命名空间：读方法透传给 VFS，而每次变更都登记撤销意图。
      
  en: >
      Transactional filesystem namespace: read methods pass through to the VFS while every mutation registers an undo intent.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:20:48.308Z"
fingerprint: 27417279d86cf988527d80c6805f9060b482885af9ee1fc92092576c1d5490fc
source:
  - path: "pyvdisk/infrastructure/disk.py"
    line: 160
    end_line: 263
apis:
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk._snapshot_dir"
    description:
      zh: >
          捕获目录子树的信息以便撤销删除。
          
      en: >
          Capture enough of a directory subtree to undo a removal.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace"
    description:
      zh: >
          把变更记录为事务意图的文件系统命名空间。
          
      en: >
          Filesystem namespace whose mutations are recorded as transaction intents.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace#write_file"
    description:
      zh: >
          事务性文件写入。
          
      en: >
          Transactional file write.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace#append_file"
    description:
      zh: >
          事务性文件追加。
          
      en: >
          Transactional file append.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace#remove"
    description:
      zh: >
          事务性文件删除。
          
      en: >
          Transactional file removal.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace#rmtree"
    description:
      zh: >
          以目录快照为背衬的事务性递归删除。
          
      en: >
          Transactional recursive tree removal backed by a directory snapshot.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace#rename"
    description:
      zh: >
          事务性重命名。
          
      en: >
          Transactional rename.
          
  - protocol: rpc
    path: "pyvdisk.infrastructure.disk.FileNamespace#makedirs"
    description:
      zh: >
          事务性递归目录创建。
          
      en: >
          Transactional recursive directory creation.
          
deps:
  - kind: dataflow
    to: pyvdisk.storage.vfs.files
    from_api: "rpc:pyvdisk.infrastructure.disk.FileNamespace#write_file"
    to_api: "rpc:pyvdisk.vfs.VFS#write_file"
    label: {zh: "委托给 VFS", en: "delegates to VFS"}
---
