---
uid: a000040b
id: pyvdisk.storage.fs.pointers
parent: pyvdisk.storage.fs
name: {zh: "块指针", en: "Block Pointers"}
description:
  zh: >
      直接与间接块指针树：解析、扩展与回收 inode 的块映射。
  en: >
      Direct and indirect block pointer tree: resolve, extend and reclaim an inode's block map.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: fde0821495837c3fa00bf19673cc22de703e3102ef613b5ee9d3469056a21ebf
source:
  - path: "pyvdisk/fs.py"
    line: 391
    end_line: 488
apis:
  - protocol: rpc
    path: "pyvdisk.fs.FS#_read_ptr"
    description:
      zh: >
          从间接块中读出一个指针。
      en: >
          Read one pointer out of an indirect block.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_write_ptr"
    description:
      zh: >
          把一个指针写入间接块。
      en: >
          Write one pointer into an indirect block.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_get_block_ptr"
    description:
      zh: >
          沿直接/单/双间接指针树把逻辑块号解析为物理块。
      en: >
          Resolve a logical block index to a physical block through the direct/single/double indirect pointer tree.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_ensure_block_ptr"
    description:
      zh: >
          为寻址某逻辑块按需分配间接块。
      en: >
          Allocate the indirect blocks needed to address a logical block.
  - protocol: rpc
    path: "pyvdisk.fs.FS#_free_all_blocks"
    description:
      zh: >
          释放 inode 引用的全部数据块与间接块。
      en: >
          Free every data and indirect block referenced by an inode.
---
