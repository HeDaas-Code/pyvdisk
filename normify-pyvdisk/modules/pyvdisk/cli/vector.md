---
uid: a0000c0d
id: pyvdisk.cli.vector
parent: pyvdisk.cli
name: {zh: "向量子命令", en: "Vector Subcommands"}
description:
  zh: >
      向量盘子命令：磁盘与集合管理，以及记录 upsert、检索与获取。
  en: >
      Vector-disk subcommands: disk and collection management plus record upsert, search and retrieval.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: 93bfec8924577ecc9e2568629fdaedff8a73379a5d29cd81a40928f400d3ad11
source:
  - path: "pyvdisk/cli.py"
    line: 573
    end_line: 625
apis:
  - protocol: rpc
    path: "pyvdisk.cli._json_arg"
    description:
      zh: >
          解析内联 JSON 参数。
      en: >
          Decode an inline JSON argument.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_create"
    description:
      zh: >
          创建向量盘。
      en: >
          Create a vector disk.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_collection"
    description:
      zh: >
          创建、列举或删除集合。
      en: >
          Create, list or drop a collection.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_upsert"
    description:
      zh: >
          向集合 upsert 记录。
      en: >
          Upsert records into a collection.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_search"
    description:
      zh: >
          执行相似度检索。
      en: >
          Run a similarity search.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_get"
    description:
      zh: >
          按 id 获取记录。
      en: >
          Fetch a record by id.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_delete"
    description:
      zh: >
          按 id 删除记录。
      en: >
          Delete a record by id.
  - protocol: rpc
    path: "pyvdisk.cli.cmd_vec_list"
    description:
      zh: >
          列出向量盘的集合。
      en: >
          List the collections of a vector disk.
---
