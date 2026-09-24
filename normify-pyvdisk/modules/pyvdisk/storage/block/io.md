---
uid: a0000203
id: pyvdisk.storage.block.io
parent: pyvdisk.storage.block
name: {zh: "定位 IO 原语", en: "Positional IO"}
description:
  zh: >
      无缓冲定位读写原语，供镜像上的所有块级与字节级访问使用。
  en: >
      Unbuffered positional read/write primitives used by every block and byte access on the image.
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:00:00Z"
fingerprint: f3dafc0720e696593d7bf2d99ff7d99856081e9e0c20a734b75f83098f1cfb80
source:
  - path: "pyvdisk/disk.py"
    line: 22
    end_line: 57
apis:
  - protocol: rpc
    path: "pyvdisk.disk._pread_all"
    description:
      zh: >
          定位读取，除 EOF 外保证读满。
      en: >
          Positional read that fills the buffer unless EOF is hit.
  - protocol: rpc
    path: "pyvdisk.disk._pwrite_all"
    description:
      zh: >
          定位写入，保证写满全部字节。
      en: >
          Positional write that guarantees every byte is written.
---
