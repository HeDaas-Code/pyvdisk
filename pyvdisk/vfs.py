"""高层虚拟文件系统 API。

提供类文件对象和路径式接口，屏蔽 inode / 块等细节。
"""

from __future__ import annotations

import os
from typing import List, Optional, Tuple

from .disk import VirtualDisk
from .fs import (
    FS,
    MAX_FILE_SIZE,
    T_DIR,
    T_FILE,
    T_SYMLINK,
    FSError,
    Stat,
    mkfs,
)


class VFS:
    """挂载在一个镜像文件上的虚拟文件系统。

    用法：
        VFS.create("/path/to/disk.vdisk", size_bytes=16 * 1024 * 1024)
        with VFS("/path/to/disk.vdisk") as vfs:
            vfs.write_file("/notes.txt", b"hello")
            print(vfs.read_file("/notes.txt"))
    """

    def __init__(self, path, block_size: int = 4096):
        # path 可以是字符串路径，也可以是已构造好的 Volume / VirtualDisk
        if isinstance(path, str):
            from .identity import validate_disk_path
            validate_disk_path(path)
            self.path = path
            self.disk = self._open_disk_or_volume(path, block_size)
        else:
            # 接受 Volume 或 VirtualDisk 实例
            self.path = getattr(path, "path", "<volume>")
            self.disk = path
        self.fs: Optional[FS] = None
        # 当前用户凭证（POSIX 风格权限检查）。uid=0 即 root，默认放行所有操作。
        # 想启用权限隔离时：vfs.uid = 1000; vfs.gid = 1000
        self.uid: int = 0
        self.gid: int = 0
        # Stack of active MetadataTransactions (outermost last) for FS undo.
        # FileNamespace mutators record before-state here so abort() can replay
        # in reverse. Push/pop is driven by MetadataTransaction.__enter__/__exit__.
        self._tx_stack: list = []
        self.enforce_perms: bool = True

    @staticmethod
    def _open_disk_or_volume(path: str, block_size: int):
        """打开镜像：若检测到它是多盘卷的成员盘，则自动打开整个卷；
        否则作为单盘 VirtualDisk 打开。

        这让所有基于 VFS 的 CLI 命令（ls/mkdir/write/cat/...）能直接
        作用于多盘卷——只需传入任意一块成员盘的路径。
        """
        from .volume import VOL_MAGIC, VolumeMeta, open_volume, VolumeError
        try:
            with open(path, "rb") as f:
                head = f.read(8)
        except OSError:
            # 文件不存在（如 create 流程），交给 VirtualDisk 处理
            return VirtualDisk(path, block_size)
        if head[:4] != VOL_MAGIC:
            # 普通单盘文件系统
            return VirtualDisk(path, block_size)
        # 是卷成员盘：读取完整元数据以获取所有成员路径
        try:
            with open(path, "rb") as f:
                raw = f.read(block_size)
            meta = VolumeMeta.from_bytes(raw)
        except Exception:
            return VirtualDisk(path, block_size)
        # 解析成员路径：优先用元数据中的路径；找不到则相对当前镜像目录按 basename 解析
        base_dir = os.path.dirname(os.path.abspath(path))
        resolved: List[str] = []
        for m in meta.members:
            p = m.path
            if os.path.exists(p):
                resolved.append(p)
            else:
                alt = os.path.join(base_dir, os.path.basename(p))
                resolved.append(alt if os.path.exists(alt) else p)
        # 确保当前镜像在成员列表中
        if os.path.abspath(path) not in [os.path.abspath(p) for p in resolved]:
            return VirtualDisk(path, block_size)
        try:
            return open_volume(resolved, block_size)
        except VolumeError:
            return VirtualDisk(path, block_size)

    # ---- 生命周期 ----
    @staticmethod
    def create(path: str, size_bytes: int, block_size: int = 4096,
               label: str = "") -> None:
        """创建并格式化一个新的虚拟磁盘。"""
        from .identity import validate_disk_path
        validate_disk_path(path)
        disk = VirtualDisk(path, block_size)
        disk.create(size_bytes)
        try:
            mkfs(disk, label=label)
        finally:
            disk.close()

    @staticmethod
    def create_volume(paths: List[str], mode: str, name: str = "",
                      stripe_size: int = 4096, disk_size: Optional[int] = None,
                      block_size: int = 4096) -> "VFS":
        """创建多盘卷并格式化文件系统。返回未挂载的 VFS。"""
        from .volume import create_volume, open_volume
        from .identity import validate_disk_path
        for path in paths:
            validate_disk_path(path)
        vol = create_volume(paths, mode, name=name, stripe_size=stripe_size,
                            block_size=block_size, disk_size=disk_size)
        try:
            mkfs(vol)
        finally:
            vol.close()
        # 返回一个可重新挂载的 VFS（带成员盘路径）
        vfs = VFS.__new__(VFS)
        vfs.path = f"<volume {name}>"
        vfs.fs = None
        vfs.uid = 0
        vfs.gid = 0
        vfs.enforce_perms = True
        vfs._volume_paths = list(paths)
        vfs._volume_block_size = block_size
        # 用一个延迟打开的 Volume 占位
        from .volume import Volume
        vol = Volume(paths, block_size=block_size)
        vfs.disk = vol
        return vfs

    def mount(self) -> "VFS":
        self.disk.open()
        self.fs = FS(self.disk).mount()
        return self

    def close(self) -> None:
        if self.fs is not None:
            self.disk.flush()
            self.fs = None
        self.disk.close()

    def __enter__(self):
        if self.fs is None:
            self.mount()
        return self

    def __exit__(self, *exc):
        self.close()

    # ---- 路径式 API ----
    def _fs_or_raise(self) -> FS:
        if self.fs is None:
            raise FSError("文件系统未挂载")
        return self.fs

    # ---- 权限检查（POSIX 风格，uid=0 即 root 放行）----
    def _perm_enabled(self) -> bool:
        return self.enforce_perms and self.uid != 0

    def _check(self, ino: int, need: int) -> None:
        """检查对 inode 的权限位 (r=4/w=2/x=1)。need=0 表示不检查。"""
        if need == 0 or not self._perm_enabled():
            return
        if not self.fs.access(ino, need, self.uid, self.gid):
            raise FSError(f"权限不足: 需要 {need} 权限 (uid={self.uid})")

    def _check_traverse(self, path: str) -> None:
        """检查路径上每个中间目录的遍历(x)权限。"""
        if not self._perm_enabled():
            return
        fs = self.fs
        parts = [p for p in path.replace("\\", "/").split("/") if p and p != "."]
        cur = ""
        for p in parts[:-1]:
            cur = cur + "/" + p if cur else "/" + p
            try:
                ino = fs.resolve(cur)
            except FSError:
                return  # 不存在，交给后续逻辑报错
            self._check(ino, 1)  # x

    def _check_parent(self, path: str, need: int) -> None:
        """检查父目录权限（通常含 x；增删还需 w）。need 为所需权限位组合。"""
        if not self._perm_enabled():
            return
        try:
            parent_ino, _name = self.fs.resolve_parent(path)
        except FSError:
            return
        self._check(parent_ino, need)

    def exists(self, path: str) -> bool:
        fs = self._fs_or_raise()
        try:
            fs.resolve(path)
            return True
        except FSError:
            return False

    def isfile(self, path: str) -> bool:
        fs = self._fs_or_raise()
        try:
            return fs.stat_path(path).is_file
        except FSError:
            return False

    def isdir(self, path: str) -> bool:
        fs = self._fs_or_raise()
        try:
            return fs.stat_path(path).is_dir
        except FSError:
            return False

    def listdir(self, path: str = "/") -> List[str]:
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path)
        self._check(ino, 4)  # r
        st = fs.stat(ino)
        if not st.is_dir:
            raise FSError(f"不是目录: {path}")
        return [name for name, _ino, _t in fs.dir_list(ino) if name not in (".", "..")]

    def listdir_with_stat(self, path: str = "/") -> List[Tuple[str, Stat]]:
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path)
        self._check(ino, 4)  # r
        out = []
        for name, child_ino, _t in fs.dir_list(ino):
            if name in (".", ".."):
                continue
            out.append((name, fs.stat(child_ino)))
        return out

    def mkdir(self, path: str, mode: int = 0o755) -> None:
        self._check_traverse(path)
        self._check_parent(path, 3)  # wx
        self._fs_or_raise().mkdir(path, mode)

    def makedirs(self, path: str, mode: int = 0o755) -> None:
        fs = self._fs_or_raise()
        parts = [p for p in path.replace("\\", "/").split("/") if p and p != "."]
        cur = ""
        for p in parts:
            cur = cur + "/" + p if cur else "/" + p
            if not self.exists(cur):
                # 每一级都要检查父目录 wx 权限
                self._check_traverse(cur)
                self._check_parent(cur, 3)
                fs.mkdir(cur, mode)

    def read_file(self, path: str) -> bytes:
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path)
        self._check(ino, 4)  # r
        st = fs.stat(ino)
        if st.is_dir:
            raise FSError(f"是目录: {path}")
        return fs.read_file(ino, 0, st.size)

    def write_file(self, path: str, data: bytes, mode: int = 0o644) -> None:
        """覆盖写入：截断后写。

        权限检查后调用 fs.write_path，由 FS 在写锁内原子完成
        解析/创建 + 截断 + 写入，避免并发覆盖写竞态。
        """
        fs = self._fs_or_raise()
        self._check_traverse(path)
        if self.exists(path):
            ino = fs.resolve(path)
            self._check(ino, 2)  # w
        else:
            self._check_parent(path, 3)  # wx
        fs.write_path(path, data, mode)

    def append_file(self, path: str, data: bytes) -> None:
        """原子追加：由 fs.append_path 在写锁内完成 解析/创建 + 读 size + 写。

        避免多线程并发追加时 stat 与 write 之间的 TOCTOU 竞态。
        """
        fs = self._fs_or_raise()
        self._check_traverse(path)
        if self.exists(path):
            ino = fs.resolve(path)
            self._check(ino, 2)  # w
        else:
            self._check_parent(path, 3)  # wx
        fs.append_path(path, data)

    def remove(self, path: str) -> None:
        self._check_traverse(path)
        self._check_parent(path, 3)  # wx
        self._fs_or_raise().unlink(path)

    def rmdir(self, path: str) -> None:
        self._check_traverse(path)
        self._check_parent(path, 3)  # wx
        self._fs_or_raise().rmdir(path)

    def rmtree(self, path: str) -> None:
        """递归删除目录树。"""
        fs = self._fs_or_raise()
        ino = fs.resolve(path)
        st = fs.stat(ino)
        if not st.is_dir:
            raise FSError(f"不是目录: {path}")
        for name, child_ino, _t in list(fs.dir_list(ino)):
            if name in (".", ".."):
                continue
            child = path.rstrip("/") + "/" + name
            cs = fs.stat(child_ino)
            if cs.is_dir:
                self.rmtree(child)
            else:
                fs.unlink(child)
        fs.rmdir(path)

    def rename(self, src: str, dst: str) -> None:
        self._check_traverse(src)
        self._check_traverse(dst)
        self._check_parent(src, 3)  # wx
        self._check_parent(dst, 3)  # wx
        self._fs_or_raise().rename(src, dst)

    def stat(self, path: str, follow: bool = True) -> Stat:
        return self._fs_or_raise().stat_path(path, follow=follow)

    def lstat(self, path: str) -> Stat:
        """不跟踪末尾符号链接（类似 lstat）。"""
        return self._fs_or_raise().lstat_path(path)

    def symlink(self, target: str, linkpath: str) -> None:
        self._check_traverse(linkpath)
        self._check_parent(linkpath, 3)  # wx
        self._fs_or_raise().symlink(target, linkpath)

    def readlink(self, path: str) -> str:
        fs = self._fs_or_raise()
        # 不跟踪：返回符号链接自身的内容
        ino = fs.resolve(path, follow=False)
        return fs.readlink(ino)

    def link(self, old_path: str, new_path: str) -> None:
        """创建硬链接。"""
        self._check_traverse(old_path)
        self._check_traverse(new_path)
        self._check_parent(new_path, 3)  # wx
        self._fs_or_raise().link(old_path, new_path)

    def chmod(self, path: str, mode: int, follow: bool = True) -> None:
        # POSIX: chmod 需要文件属主或 root
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path, follow=follow)
        if self._perm_enabled():
            st = fs.stat(ino)
            if st.uid != self.uid:
                raise FSError(f"权限不足: chmod 需要属主 (uid={self.uid})")
        fs.chmod(ino, mode)

    def chown(self, path: str, uid: int = -1, gid: int = -1, follow: bool = True) -> None:
        # POSIX: chown 需要 root
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path, follow=follow)
        if self._perm_enabled():
            raise FSError("权限不足: chown 需要 root")
        fs.chown(ino, uid, gid)

    def utime(self, path: str, atime: int = -1, mtime: int = -1, follow: bool = True) -> None:
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path, follow=follow)
        if self._perm_enabled():
            st = fs.stat(ino)
            if st.uid != self.uid:
                raise FSError(f"权限不足: utime 需要属主 (uid={self.uid})")
        fs.utime(ino, atime, mtime)

    def access(self, path: str, mode: int, uid: int = 0, gid: int = 0) -> bool:
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path)
        return fs.access(ino, mode, uid, gid)

    def truncate(self, path: str, size: int) -> None:
        fs = self._fs_or_raise()
        self._check_traverse(path)
        ino = fs.resolve(path)
        self._check(ino, 2)  # w
        fs.truncate(ino, size)

    # ---- 类文件对象 ----
    def open(self, path: str, mode: str = "rb") -> "VFile":
        return VFile(self, path, mode)

    # ---- 宿主机 <-> 虚拟磁盘 互拷 ----
    def import_host_file(self, host_path: str, vpath: str) -> None:
        with open(host_path, "rb") as f:
            data = f.read()
        if len(data) > MAX_FILE_SIZE:
            raise FSError(f"文件过大，单文件上限 {MAX_FILE_SIZE} 字节")
        self.write_file(vpath, data)

    def export_to_host(self, vpath: str, host_path: str) -> None:
        data = self.read_file(vpath)
        with open(host_path, "wb") as f:
            f.write(data)

    def import_host_tree(self, host_dir: str, vdir: str) -> None:
        if not self.exists(vdir):
            self.makedirs(vdir)
        for root, dirs, files in os.walk(host_dir):
            rel = os.path.relpath(root, host_dir)
            target_root = vdir if rel == "." else vdir.rstrip("/") + "/" + rel.replace(os.sep, "/")
            if not self.exists(target_root):
                self.makedirs(target_root)
            for fn in files:
                hp = os.path.join(root, fn)
                vp = target_root.rstrip("/") + "/" + fn
                self.import_host_file(hp, vp)

    def walk(self, top: str = "/"):
        """类似 os.walk 的生成器。"""
        fs = self._fs_or_raise()
        dirs = []
        files = []
        try:
            ino = fs.resolve(top)
        except FSError:
            return
        for name, child_ino, _t in fs.dir_list(ino):
            if name in (".", ".."):
                continue
            st = fs.stat(child_ino)
            if st.is_dir:
                dirs.append(name)
            else:
                files.append(name)
        yield top, dirs, files
        for d in dirs:
            yield from self.walk(top.rstrip("/") + "/" + d)

    # ---- 空间 / 一致性 ----
    def statfs(self) -> dict:
        """文件系统使用情况（类似 statfs）。"""
        return self._fs_or_raise().statfs()

    def df(self) -> dict:
        """磁盘使用摘要（人类可读字段）。"""
        info = self.statfs()
        used = info["blocks"] - info["bfree"]
        return {
            "total_bytes": info["blocks"] * info["bsize"],
            "used_bytes": used * info["bsize"],
            "free_bytes": info["bfree"] * info["bsize"],
            "total_inodes": info["files"],
            "free_inodes": info["ffree"],
            "block_size": info["bsize"],
        }

    def du(self, path: str = "/") -> int:
        """递归计算路径下所有文件数据的字节数（不含目录元数据开销）。"""
        fs = self._fs_or_raise()
        total = 0
        for top, dirs, files in self.walk(path):
            for fn in files:
                try:
                    st = fs.stat_path(top.rstrip("/") + "/" + fn)
                    total += st.size
                except FSError:
                    pass
        return total

    def fsck(self, repair: bool = False) -> dict:
        """检查文件系统一致性。"""
        return self._fs_or_raise().fsck(repair=repair)

    def grow(self, new_size: int) -> None:
        """扩大虚拟磁盘容量（在线，不破坏数据）。"""
        from .fs import grow as _grow
        _grow(self.disk, new_size)
        # 重新挂载以刷新超级块缓存
        self.fs = FS(self.disk).mount()


class VFile:
    """类文件对象，支持读写定位。"""

    def __init__(self, vfs: VFS, path: str, mode: str = "rb"):
        self.vfs = vfs
        self.path = path
        self.mode = mode
        self._closed = False
        self._pos = 0
        self._ino: Optional[int] = None
        fs = vfs._fs_or_raise()

        if ("w" in mode) and ("+" not in mode):
            # 纯写（不含 +）：截断或创建
            if vfs.exists(path):
                ino = fs.resolve(path)
                fs.truncate(ino, 0)
            else:
                ino = fs.create(path)
            self._ino = ino
        elif "a" in mode:
            if vfs.exists(path):
                ino = fs.resolve(path)
                st = fs.stat(ino)
                self._pos = st.size
            else:
                ino = fs.create(path)
            self._ino = ino
        elif "+" in mode:
            # r+/w+/a+：可读可写，不截断；文件不存在则报错（按 Python 内置行为）
            if vfs.exists(path):
                self._ino = fs.resolve(path)
            elif "w" in mode:
                self._ino = fs.create(path)
            else:
                raise FSError(f"文件不存在: {path}")
        else:
            # 纯读模式（不含 w/a/+）：文件不存在则报错
            if vfs.exists(path):
                self._ino = fs.resolve(path)
            else:
                raise FSError(f"文件不存在: {path}")

    @property
    def ino(self) -> int:
        if self._ino is None:
            raise FSError("文件未打开")
        return self._ino

    def read(self, size: int = -1) -> bytes:
        if "r" not in self.mode and "+" not in self.mode:
            raise FSError("文件未以读模式打开")
        fs = self.vfs._fs_or_raise()
        st = fs.stat(self.ino)
        remaining = st.size - self._pos
        if remaining <= 0:
            return b""
        length = remaining if size < 0 else min(size, remaining)
        data = fs.read_file(self.ino, self._pos, length)
        self._pos += len(data)
        return data

    def readall(self) -> bytes:
        return self.read(-1)

    def write(self, data: bytes) -> int:
        if "w" not in self.mode and "a" not in self.mode and "+" not in self.mode:
            raise FSError("文件未以写模式打开")
        fs = self.vfs._fs_or_raise()
        n = fs.write_file(self.ino, self._pos, data)
        self._pos += n
        return n

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        elif whence == 2:
            st = self.vfs._fs_or_raise().stat(self.ino)
            self._pos = st.size + offset
        return self._pos

    def tell(self) -> int:
        return self._pos

    def truncate(self, size: Optional[int] = None) -> None:
        if size is None:
            size = self._pos
        self.vfs._fs_or_raise().truncate(self.ino, size)

    def flush(self) -> None:
        self.vfs._fs_or_raise().disk.flush()

    def close(self) -> None:
        if not self._closed:
            self.flush()
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __iter__(self):
        while True:
            chunk = self.read(4096)
            if not chunk:
                break
            yield chunk
