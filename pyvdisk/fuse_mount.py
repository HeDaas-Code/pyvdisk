"""可选的 FUSE 挂载支持。

把虚拟磁盘挂载到一个本地目录，像访问普通文件系统一样访问它。
FUSE 运行在用户态，**不需要 root 权限**（需要系统已安装 fuse 并允许当前用户使用）。

依赖：pip install fusepy
（在 Linux 上还需要内核 fuse 支持；macOS 需安装 macFUSE）

如果 fusepy 不可用，本模块的 mount() 会抛出带说明的 ImportError，
而 VFS / API 仍可正常使用。
"""

# pylint: disable=import-error
# fusepy 是可选依赖（pip install pyvdisk[fuse]），所有 import fuse 都刻意延迟到
# 函数内部，因此未安装时本模块依然可导入 -- 这不是缺陷。

from __future__ import annotations

import os
import stat as _stat
import time
from typing import Any, Optional

from .fs import FSError, T_DIR, T_FILE, T_SYMLINK
from .vfs import VFS


def _have_fuse() -> bool:
    try:
        import fuse  # noqa: F401
        return True
    except Exception:
        return False


class _VFuseOperations:
    """FUSE 操作实现。延迟导入 fuse 以便在没有 fusepy 时模块仍可导入。"""

    def __init__(self, vfs: VFS):
        self.vfs = vfs

    # 以下方法在 _build_class 中动态挂到由 fuse.Operations 派生的类上
    def _getattr(self, path: str):
        from fuse import FuseOSError, ENOENT

        fs = self.vfs._fs_or_raise()
        try:
            # FUSE 的 getattr 不应跟踪末尾符号链接（内核负责跟踪）
            st = fs.stat_path(path, follow=False)
        except FSError:
            raise FuseOSError(ENOENT)
        now = int(time.time())
        mode = st.mode
        if st.is_dir:
            mode |= _stat.S_IFDIR
        elif st.is_symlink:
            mode |= _stat.S_IFLNK
        else:
            mode |= _stat.S_IFREG
        return {
            "st_ino": st.ino,
            "st_mode": mode,
            "st_dev": 0,
            "st_nlink": st.nlink,
            "st_uid": os.getuid() if hasattr(os, "getuid") else st.uid,
            "st_gid": os.getgid() if hasattr(os, "getgid") else st.gid,
            "st_size": st.size,
            "st_atime": st.atime or now,
            "st_mtime": st.mtime or now,
            "st_ctime": st.ctime or now,
        }

    def _readdir(self, path: str, fh: Any):
        fs = self.vfs._fs_or_raise()
        try:
            ino = fs.resolve(path)
        except FSError:
            return ["." + "_raise"]
        entries = [".", ".."]
        for name, _i, _t in fs.dir_list(ino):
            if name not in (".", ".."):
                entries.append(name)
        return entries

    def _read(self, path: str, size: int, offset: int, fh: Any):
        fs = self.vfs._fs_or_raise()
        try:
            ino = fs.resolve(path)
        except FSError:
            return b""
        return fs.read_file(ino, offset, size)

    def _write(self, path: str, data: bytes, offset: int, fh: Any):
        fs = self.vfs._fs_or_raise()
        try:
            ino = fs.resolve(path)
        except FSError:
            ino = fs.create(path)
        return fs.write_file(ino, offset, data)

    def _create(self, path: str, mode: int, fi: Any = None):
        fs = self.vfs._fs_or_raise()
        if not self.vfs.exists(path):
            fs.create(path, mode & 0o777)
        return 0

    def _mkdir(self, path: str, mode: int):
        self.vfs._fs_or_raise().mkdir(path, mode & 0o777)
        return 0

    def _rmdir(self, path: str):
        self.vfs._fs_or_raise().rmdir(path)
        return 0

    def _unlink(self, path: str):
        self.vfs._fs_or_raise().unlink(path)
        return 0

    def _rename(self, old: str, new: str):
        self.vfs._fs_or_raise().rename(old, new)
        return 0

    def _truncate(self, path: str, length: int, fh: Any = None):
        fs = self.vfs._fs_or_raise()
        try:
            ino = fs.resolve(path)
        except FSError:
            return 0
        fs.truncate(ino, length)
        return 0

    def _symlink(self, target: str, linkpath: str):
        self.vfs._fs_or_raise().symlink(target, linkpath)
        return 0

    def _readlink(self, path: str):
        from fuse import FuseOSError, EINVAL

        fs = self.vfs._fs_or_raise()
        try:
            # lstat semantics: the link's own inode. Following it here resolved to the
            # target -- a regular file -- and readlink then raised, so every symlink
            # read through FUSE reported EINVAL.
            ino = fs.resolve(path, follow=False)
            return fs.readlink(ino)
        except FSError:
            raise FuseOSError(EINVAL)

    def _open(self, path: str, flags: int):
        return 0

    def _release(self, path: str, fh: Any):
        return 0

    def _chmod(self, path: str, mode: int):
        from .fs import FS  # 仅类型
        fs = self.vfs._fs_or_raise()
        try:
            ino = fs.resolve(path)
        except FSError:
            return 0
        inode = fs.read_inode(ino)
        inode.mode = mode & 0o7777
        fs.write_inode(ino, inode)
        return 0


def _build_fuse_class():
    """构建一个继承自 fuse.Operations 的类（延迟导入）。"""
    from fuse import FuseOSError, Operations, LoggingMixIn  # type: ignore

    ops = _VFuseOperations

    class _VFuse(LoggingMixIn, Operations):
        def __init__(self, vfs: VFS):
            self._impl = ops(vfs)
            self.vfs = vfs

        def getattr(self, path, fh=None):
            return self._impl._getattr(path)

        def readdir(self, path, fh):
            return self._impl._readdir(path, fh)

        def read(self, path, size, offset, fh):
            return self._impl._read(path, size, offset, fh)

        def write(self, path, data, offset, fh):
            return self._impl._write(path, data, offset, fh)

        def create(self, path, mode, fi=None):
            return self._impl._create(path, mode, fi)

        def mkdir(self, path, mode):
            return self._impl._mkdir(path, mode)

        def rmdir(self, path):
            return self._impl._rmdir(path)

        def unlink(self, path):
            return self._impl._unlink(path)

        def rename(self, old, new):
            return self._impl._rename(old, new)

        def truncate(self, path, length, fh=None):
            return self._impl._truncate(path, length, fh)

        def symlink(self, target, linkpath):
            return self._impl._symlink(target, linkpath)

        def readlink(self, path):
            return self._impl._readlink(path)

        def open(self, path, flags):
            return self._impl._open(path, flags)

        def release(self, path, flags, fh=None):
            return self._impl._release(path, fh)

        def chmod(self, path, mode):
            return self._impl._chmod(path, mode)

        # 关闭 FUSE 自身的 statfs 也返回合理值
        def statfs(self, path):
            sb = self.vfs._fs_or_raise().sb
            return {
                "f_bsize": sb.block_size,
                "f_frsize": sb.block_size,
                "f_blocks": sb.total_blocks,
                "f_bfree": sb.total_blocks,
                "f_bavail": sb.total_blocks,
                "f_files": sb.total_inodes,
                "f_ffree": sb.total_inodes,
                "f_favail": sb.total_inodes,
            }

    return _VFuse


def mount(vfs: VFS, mountpoint: str, foreground: bool = False, **opts) -> None:
    """把 vfs 挂载到 mountpoint 目录。阻塞调用。

    不需要 root。前提：
      - 已安装 fusepy（pip install fusepy）
      - 系统有 /dev/fuse 且当前用户有权使用
      - macOS 需 macFUSE
    """
    if not _have_fuse():
        raise ImportError(
            "未安装 fusepy。请运行：pip install fusepy\n"
            "（Linux 还需要 /dev/fuse；macOS 需要 macFUSE）。\n"
            "不使用 FUSE 也可以通过 VFS API 操作虚拟磁盘。"
        )
    if not os.path.isdir(mountpoint):
        raise FSError(f"挂载点不是目录: {mountpoint}")

    FuseClass = _build_fuse_class()
    fuse_ops = FuseClass(vfs)
    # FUSE 主循环会阻塞
    fuse_ops.main = _patched_main(fuse_ops, mountpoint, foreground, **opts)
    fuse_ops.main()


def _patched_main(fuse_ops, mountpoint, foreground, **opts):
    from fuse import FUSE  # type: ignore

    def _main():
        FUSE(fuse_ops, mountpoint, foreground=foreground, nothreads=True, **opts)

    return _main


def mount_in_thread(vfs: VFS, mountpoint: str, **opts):
    """在后台线程挂载，返回 (thread, ready_event)。

    用于测试或交互场景。调用方负责最终 unmount（结束线程）。
    """
    import threading

    if not _have_fuse():
        raise ImportError("未安装 fusepy，无法挂载。")

    ready = threading.Event()
    err: list = []

    def _run():
        try:
            FuseClass = _build_fuse_class()
            from fuse import FUSE  # type: ignore
            ops = FuseClass(vfs)
            ready.set()
            FUSE(ops, mountpoint, foreground=False, nothreads=True, **opts)
        except Exception as e:
            err.append(e)
            ready.set()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    ready.wait(timeout=5)
    if err:
        raise err[0]
    return t, ready
