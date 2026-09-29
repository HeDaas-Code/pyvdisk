---
uid: a0000411
id: pyvdisk.storage.fs.mutate
parent: pyvdisk.storage.fs
name: {zh: "删除与重命名", en: "Delete and Rename"}
description:
  zh: >
      删除与重命名：unlink、rmdir、节点解绑与目标替换。
      
  en: >
      Deletion and rename: unlink, rmdir, node detach and destination replacement.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:48.423Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 780
    end_line: 858
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#unlink"
    description:
      zh: >
          删除一个名字；最后一个链接消失时释放 inode。
          
      en: >
          Remove one name; the inode is freed when the last link disappears.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#rmdir"
    description:
      zh: >
          删除空目录。
          
      en: >
          Remove an empty directory.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#_remove_node"
    description:
      zh: >
          把名字与 inode 解绑，无链接时释放 inode。
          
      en: >
          Detach a name from its inode and drop the inode when unlinked.
          
  - protocol: rpc
    path: "pyvdisk.fs.FS#rename"
    description:
      zh: >
          重命名或移动路径，并替换目标目录项。
          
      en: >
          Rename or move a path, replacing the destination entry.
          
deps:
  - kind: call
    to: pyvdisk.storage.fs.pointers
    from_api: "rpc:pyvdisk.fs.FS#_remove_node"
    to_api: "rpc:pyvdisk.fs.FS#_free_all_blocks"
    label: {zh: "回收数据块", en: "reclaims blocks"}
---
