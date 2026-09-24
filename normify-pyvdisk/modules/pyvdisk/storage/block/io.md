---
uid: a0000203
id: pyvdisk.storage.block.io
parent: pyvdisk.storage.block
name: {zh: "定位 IO 原语", en: "Positional IO"}
description:
  zh: >
      无缓冲定位读写原语，供镜像上的所有块级与字节级访问使用；经由平台适配层，同一份代码在 Windows 上也能跑。
      
  en: >
      Unbuffered positional read/write primitives used by every block and byte access on the image, routed through the platform layer so the same code runs on Windows.
      
revision: 2c9009ba74afb515d301cc96e1946087268479a2
updated_at: "2026-09-24T11:41:14.329Z"
fingerprint: 88da0b2f3ce22b186edf88eab3d800c8e50671236a9ed1b9dbed478ff6837d16
source:
  - path: "pyvdisk/disk.py"
    line: 22
    end_line: 57
apis:
  - protocol: rpc
    path: "pyvdisk.disk._pread_all"
    description:
      zh: >
          定位读取，除 EOF 外保证读满。转发给 compat.pread，因此 Windows 上得到的是加锁的 seek+read，而不是 os.pread。
          
      en: >
          Positional read that fills the buffer unless EOF is hit. Delegates to compat.pread, so Windows gets a lock-protected seek+read instead of os.pread.
          
  - protocol: rpc
    path: "pyvdisk.disk._pwrite_all"
    description:
      zh: >
          定位写入，保证写满全部字节。转发给 compat.pwrite，在 Windows 上用同一把锁串行化 seek+write。
          
      en: >
          Positional write that guarantees every byte is written. Delegates to compat.pwrite, which serialises seek+write on Windows.
          
deps:
  - kind: call
    to: pyvdisk.platform.positional
    from_api: "rpc:pyvdisk.disk._pread_all"
    to_api: "rpc:pyvdisk.compat.pread"
    label: {zh: "定位读取", en: "positioned read"}
  - kind: call
    to: pyvdisk.platform.positional
    from_api: "rpc:pyvdisk.disk._pwrite_all"
    to_api: "rpc:pyvdisk.compat.pwrite"
    label: {zh: "定位写入", en: "positioned write"}
---
