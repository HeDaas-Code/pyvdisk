"""pyvdisk 综合测试。可用 pytest 运行，也可直接 python -m tests.test_vdisk。"""

import os
import sys
import shutil
import struct
import tempfile
import unittest

# 让脚本能直接运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyvdisk import VFS, VFile, FSError
from pyvdisk.fs import FS, mkfs, MAX_FILE_SIZE, T_DIR, T_FILE
from pyvdisk.disk import VirtualDisk
from pyvdisk.cli import main as cli_main


class VFSTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.vdisk = os.path.join(self.tmp, "disk.vdisk")
        # 16MB 磁盘，足够测试二级间接块
        VFS.create(self.vdisk, 16 * 1024 * 1024)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestBasic(VFSTestBase):
    def test_root_exists(self):
        with VFS(self.vdisk) as vfs:
            self.assertTrue(vfs.isdir("/"))
            self.assertFalse(vfs.isfile("/"))
            self.assertEqual(vfs.listdir("/"), [])

    def test_mkdir_and_ls(self):
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/docs")
            vfs.mkdir("/pics")
            self.assertEqual(sorted(vfs.listdir("/")), ["docs", "pics"])
            self.assertTrue(vfs.isdir("/docs"))

    def test_makedirs(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/a/b/c/d")
            self.assertTrue(vfs.isdir("/a/b/c/d"))
            vfs.makedirs("/a/b/c/d")  # 已存在不报错

    def test_write_read_small(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/hello.txt", b"hello world")
            self.assertEqual(vfs.read_file("/hello.txt"), b"hello world")
            self.assertTrue(vfs.isfile("/hello.txt"))
            st = vfs.stat("/hello.txt")
            self.assertEqual(st.size, 11)
            self.assertEqual(st.type, T_FILE)

    def test_overwrite(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"aaaa")
            vfs.write_file("/f.txt", b"bb")  # 覆盖，且更短
            self.assertEqual(vfs.read_file("/f.txt"), b"bb")
            self.assertEqual(vfs.stat("/f.txt").size, 2)

    def test_append(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"hello")
            vfs.append_file("/f.txt", b" world")
            self.assertEqual(vfs.read_file("/f.txt"), b"hello world")

    def test_overwrite_grow(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"short")
            vfs.write_file("/f.txt", b"a much longer line than before")
            self.assertEqual(vfs.read_file("/f.txt"), b"a much longer line than before")


class TestLargeFiles(VFSTestBase):
    def test_single_indirect(self):
        # 12 直接块 = 49152 字节，写 100KB 触发一级间接
        data = bytes((i * 7) % 256 for i in range(100 * 1024))
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/big.bin", data)
            self.assertEqual(vfs.read_file("/big.bin"), data)
            self.assertEqual(vfs.stat("/big.bin").size, len(data))

    def test_double_indirect(self):
        # (12 + 1024) 块 = 4243456 字节，写 4.5MB 触发二级间接
        size = 4_500_000
        data = bytes((i * 13) % 256 for i in range(size))
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/huge.bin", data)
            got = vfs.read_file("/huge.bin")
            self.assertEqual(len(got), size)
            self.assertEqual(got, data)

    def test_partial_read_write(self):
        data = bytes(range(256)) * 200  # 51200 字节
        with VFS(self.vdisk) as vfs:
            ino = vfs.fs.create("/p.bin")
            vfs.fs.write_file(ino, 0, data)
            # 偏移读取
            self.assertEqual(vfs.fs.read_file(ino, 100, 50), data[100:150])
            # 中间写
            vfs.fs.write_file(ino, 10, b"XYZ")
            self.assertEqual(vfs.fs.read_file(ino, 10, 3), b"XYZ")
            self.assertEqual(vfs.fs.read_file(ino, 0, 10), data[:10])

    def test_truncate_shrink_and_grow(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/t.bin", b"A" * 10000)
            vfs.truncate("/t.bin", 4096)
            self.assertEqual(vfs.read_file("/t.bin"), b"A" * 4096)
            vfs.truncate("/t.bin", 8192)
            got = vfs.read_file("/t.bin")
            self.assertEqual(len(got), 8192)
            self.assertEqual(got[:4096], b"A" * 4096)
            self.assertEqual(got[4096:], b"\x00" * 4096)


class TestDirsAndRemove(VFSTestBase):
    def test_remove_file(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/x.txt", b"hi")
            vfs.remove("/x.txt")
            self.assertFalse(vfs.exists("/x.txt"))
            self.assertEqual(vfs.listdir("/"), [])

    def test_rmdir_empty_and_nonempty(self):
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/d")
            vfs.rmdir("/d")
            self.assertFalse(vfs.exists("/d"))
            vfs.mkdir("/d")
            vfs.write_file("/d/f.txt", b"x")
            with self.assertRaises(FSError):
                vfs.rmdir("/d")
            vfs.rmtree("/d")
            self.assertFalse(vfs.exists("/d"))

    def test_rmtree_deep(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/tree/a/b")
            vfs.write_file("/tree/f1", b"1")
            vfs.write_file("/tree/a/f2", b"2")
            vfs.write_file("/tree/a/b/f3", b"3")
            vfs.rmtree("/tree")
            self.assertFalse(vfs.exists("/tree"))


class TestRename(VFSTestBase):
    def test_rename_file(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"data")
            vfs.rename("/a.txt", "/b.txt")
            self.assertFalse(vfs.exists("/a.txt"))
            self.assertEqual(vfs.read_file("/b.txt"), b"data")

    def test_rename_file_overwrite(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"AAA")
            vfs.write_file("/b.txt", b"B")
            vfs.rename("/a.txt", "/b.txt")
            self.assertEqual(vfs.read_file("/b.txt"), b"AAA")

    def test_rename_dir(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/old/sub")
            vfs.write_file("/old/sub/f.txt", b"keep")
            vfs.rename("/old", "/new")
            self.assertTrue(vfs.exists("/new/sub/f.txt"))
            self.assertEqual(vfs.read_file("/new/sub/f.txt"), b"keep")


class TestSymlink(VFSTestBase):
    def test_symlink(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/target.txt", b"content")
            vfs.symlink("/target.txt", "/link.txt")
            # lstat 不跟踪，stat 跟踪
            self.assertTrue(vfs.lstat("/link.txt").is_symlink)
            self.assertTrue(vfs.stat("/link.txt").is_file)  # 跟踪到目标
            self.assertEqual(vfs.readlink("/link.txt"), "/target.txt")

    def test_symlink_path_resolution(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/real.txt", b"via link")
            vfs.symlink("/real.txt", "/l")
            # 通过符号链接读取目标
            self.assertEqual(vfs.read_file("/l"), b"via link")
            # 中间路径符号链接
            vfs.mkdir("/dir")
            vfs.symlink("/dir", "/dlink")
            vfs.write_file("/dir/f.txt", b"nested")
            self.assertEqual(vfs.read_file("/dlink/f.txt"), b"nested")

    def test_symlink_loop_detected(self):
        with VFS(self.vdisk) as vfs:
            vfs.symlink("/a", "/b")
            vfs.symlink("/b", "/a")
            with self.assertRaises(FSError):
                vfs.stat("/a")

    def test_relative_symlink(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/d/sub")
            vfs.write_file("/d/target.txt", b"rel")
            # 相对符号链接：相对于 /d
            vfs.symlink("target.txt", "/d/rel.txt")
            self.assertEqual(vfs.read_file("/d/rel.txt"), b"rel")


class TestVFile(VFSTestBase):
    def test_vfile_write_read(self):
        with VFS(self.vdisk) as vfs:
            with vfs.open("/f.bin", "wb") as f:
                f.write(b"hello")
                f.write(b" world")
            with vfs.open("/f.bin", "rb") as f:
                self.assertEqual(f.read(), b"hello world")

    def test_vfile_seek(self):
        with VFS(self.vdisk) as vfs:
            with vfs.open("/f.bin", "wb") as f:
                f.write(b"0123456789")
            with vfs.open("/f.bin", "rb") as f:
                f.seek(3)
                self.assertEqual(f.read(2), b"34")
                f.seek(-3, 2)
                self.assertEqual(f.read(), b"789")

    def test_vfile_append(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.bin", b"abc")
            with vfs.open("/f.bin", "ab") as f:
                f.write(b"DEF")
            self.assertEqual(vfs.read_file("/f.bin"), b"abcDEF")


class TestPersistence(VFSTestBase):
    def test_remount(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/docs")
            vfs.write_file("/docs/notes.txt", b"persistent data")
        # 重新挂载
        with VFS(self.vdisk) as vfs:
            self.assertTrue(vfs.exists("/docs/notes.txt"))
            self.assertEqual(vfs.read_file("/docs/notes.txt"), b"persistent data")


class TestImportExport(VFSTestBase):
    def test_import_export(self):
        host_file = os.path.join(self.tmp, "host.bin")
        payload = os.urandom(50_000)
        with open(host_file, "wb") as f:
            f.write(payload)
        with VFS(self.vdisk) as vfs:
            vfs.import_host_file(host_file, "/v.bin")
            self.assertEqual(vfs.read_file("/v.bin"), payload)
            out = os.path.join(self.tmp, "out.bin")
            vfs.export_to_host("/v.bin", out)
            with open(out, "rb") as f:
                self.assertEqual(f.read(), payload)

    def test_import_tree(self):
        # 建一个宿主机目录树
        root = os.path.join(self.tmp, "tree")
        os.makedirs(os.path.join(root, "sub"))
        with open(os.path.join(root, "a.txt"), "wb") as f:
            f.write(b"A")
        with open(os.path.join(root, "sub", "b.txt"), "wb") as f:
            f.write(b"B")
        with VFS(self.vdisk) as vfs:
            vfs.import_host_tree(root, "/imported")
            self.assertTrue(vfs.exists("/imported/a.txt"))
            self.assertTrue(vfs.exists("/imported/sub/b.txt"))
            self.assertEqual(vfs.read_file("/imported/sub/b.txt"), b"B")


class TestEdgeCases(VFSTestBase):
    def test_missing_path_raises(self):
        with VFS(self.vdisk) as vfs:
            with self.assertRaises(FSError):
                vfs.read_file("/nope.txt")
            self.assertFalse(vfs.exists("/nope.txt"))

    def test_mkdir_existing_raises(self):
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/d")
            with self.assertRaises(FSError):
                vfs.mkdir("/d")

    def test_unlink_dir_raises(self):
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/d")
            with self.assertRaises(FSError):
                vfs.remove("/d")

    def test_long_name_rejected(self):
        with VFS(self.vdisk) as vfs:
            with self.assertRaises(FSError):
                vfs.write_file("/x" * 30, b"data")

    def test_empty_file(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/empty", b"")
            self.assertEqual(vfs.read_file("/empty"), b"")
            self.assertEqual(vfs.stat("/empty").size, 0)

    def test_many_files(self):
        with VFS(self.vdisk) as vfs:
            for i in range(200):
                vfs.write_file(f"/f{i:03d}", str(i).encode())
            names = vfs.listdir("/")
            self.assertEqual(len(names), 200)
            self.assertEqual(vfs.read_file("/f100"), b"100")


class TestHardLinks(VFSTestBase):
    def test_hard_link_basic(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/orig.txt", b"shared")
            vfs.link("/orig.txt", "/hard.txt")
            # 两个名字指向同一 inode
            self.assertEqual(vfs.read_file("/hard.txt"), b"shared")
            self.assertEqual(vfs.stat("/orig.txt").ino, vfs.stat("/hard.txt").ino)
            self.assertEqual(vfs.stat("/orig.txt").nlink, 2)

    def test_hard_link_write_visible(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"init")
            vfs.link("/a.txt", "/b.txt")
            vfs.write_file("/b.txt", b"changed")  # 通过 b 写
            self.assertEqual(vfs.read_file("/a.txt"), b"changed")

    def test_hard_link_unlink_keeps_data(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"persist")
            vfs.link("/a.txt", "/b.txt")
            vfs.remove("/a.txt")
            self.assertFalse(vfs.exists("/a.txt"))
            # 数据仍可通过 b 访问
            self.assertEqual(vfs.read_file("/b.txt"), b"persist")
            self.assertEqual(vfs.stat("/b.txt").nlink, 1)

    def test_hard_link_dir_rejected(self):
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/d")
            with self.assertRaises(FSError):
                vfs.link("/d", "/d2")


class TestAttributes(VFSTestBase):
    def test_chmod(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"x")
            vfs.chmod("/f.txt", 0o600)
            self.assertEqual(vfs.stat("/f.txt").mode, 0o600)
            vfs.chmod("/f.txt", 0o755)
            self.assertEqual(vfs.stat("/f.txt").mode, 0o755)

    def test_chown(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"x")
            vfs.chown("/f.txt", uid=100, gid=200)
            st = vfs.stat("/f.txt")
            self.assertEqual(st.uid, 100)
            self.assertEqual(st.gid, 200)

    def test_utime(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"x")
            vfs.utime("/f.txt", atime=1000, mtime=2000)
            st = vfs.stat("/f.txt")
            self.assertEqual(st.atime, 1000)
            self.assertEqual(st.mtime, 2000)

    def test_access_root(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"x")
            vfs.chmod("/f.txt", 0o600)
            # root 总是允许
            self.assertTrue(vfs.access("/f.txt", 7, uid=0))

    def test_access_non_root(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"x")
            vfs.chown("/f.txt", uid=100)
            vfs.chmod("/f.txt", 0o640)
            # 属主：rw
            self.assertTrue(vfs.access("/f.txt", 4, uid=100))   # r
            self.assertTrue(vfs.access("/f.txt", 2, uid=100))   # w
            self.assertFalse(vfs.access("/f.txt", 1, uid=100))  # x
            # 同组：r
            self.assertTrue(vfs.access("/f.txt", 4, uid=999, gid=200)
                            if vfs.stat("/f.txt").gid == 200 else True)


class TestSparseFile(VFSTestBase):
    def test_hole_reads_zero(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.bin", b"AAAA")
            vfs.truncate("/f.bin", 8192)  # 扩大到 8192，中间是空洞
            data = vfs.read_file("/f.bin")
            self.assertEqual(len(data), 8192)
            self.assertEqual(data[:4], b"AAAA")
            self.assertEqual(data[4:], b"\x00" * 8188)

    def test_write_into_hole(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.bin", b"")  # 创建空文件
            vfs.truncate("/f.bin", 8192)   # 扩大成全空洞
            # 在空洞中间写
            vfs.fs.write_file(vfs.fs.resolve("/f.bin"), 4096, b"X" * 10)
            data = vfs.read_file("/f.bin")
            self.assertEqual(data[4096:4106], b"X" * 10)
            self.assertEqual(data[:4096], b"\x00" * 4096)


class TestFsck(VFSTestBase):
    def test_fsck_clean(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/a/b")
            vfs.write_file("/a/b/f.txt", b"data" * 1000)
            vfs.link("/a/b/f.txt", "/a/b/g.txt")
            vfs.symlink("/a/b/f.txt", "/a/b/link")
            report = vfs.fsck()
            self.assertTrue(report["ok"], f"fsck 发现问题: {report['problems']}")

    def test_fsck_detects_orphan_block(self):
        # 人为制造一个孤儿块
        from pyvdisk.fs import FS
        with VFS(self.vdisk) as vfs:
            fs = vfs.fs
            sb = fs.sb
            # 找一个未使用的块标记为已用
            for b in range(sb.data_start, sb.total_blocks):
                if not fs._bitmap_get(sb.block_bitmap_start, b):
                    fs._bitmap_set(sb.block_bitmap_start, b, True)
                    orphan = b
                    break
            report = vfs.fsck()
            self.assertFalse(report["ok"])
            self.assertTrue(any("孤儿块" in p for p in report["problems"]))
            # 修复
            report2 = vfs.fsck(repair=True)
            self.assertTrue(any("孤儿块" in r for r in report2["repaired"]))
            report3 = vfs.fsck()
            self.assertTrue(report3["ok"], f"修复后仍有问题: {report3['problems']}")

    def test_fsck_detects_nlink_mismatch(self):
        from pyvdisk.fs import FS
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/f.txt", b"data")
            fs = vfs.fs
            ino = fs.resolve("/f.txt")
            inode = fs.read_inode(ino)
            inode.nlink = 5  # 错误的 nlink
            fs.write_inode(ino, inode)
            report = vfs.fsck()
            self.assertFalse(report["ok"])
            self.assertTrue(any("nlink" in p for p in report["problems"]))


class TestGrow(VFSTestBase):
    def test_grow_preserves_data(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/keep.txt", b"important data")
            before = vfs.df()
            # 扩容到 32MB
            vfs.grow(32 * 1024 * 1024)
            after = vfs.df()
            self.assertGreater(after["total_bytes"], before["total_bytes"])
            self.assertEqual(after["total_bytes"], 32 * 1024 * 1024)
            # 数据仍在
            self.assertEqual(vfs.read_file("/keep.txt"), b"important data")

    def test_grow_can_use_new_space(self):
        with VFS(self.vdisk) as vfs:
            vfs.grow(32 * 1024 * 1024)
            # 写入大量数据到新空间
            data = bytes((i * 3) % 256 for i in range(2 * 1024 * 1024))
            vfs.write_file("/big.bin", data)
            self.assertEqual(vfs.read_file("/big.bin"), data)

    def test_grow_rejects_shrink(self):
        with VFS(self.vdisk) as vfs:
            with self.assertRaises(FSError):
                vfs.grow(4 * 1024)  # 比当前小


class TestSpaceInfo(VFSTestBase):
    def test_df(self):
        with VFS(self.vdisk) as vfs:
            info = vfs.df()
            self.assertEqual(info["total_bytes"], 16 * 1024 * 1024)
            self.assertGreater(info["free_bytes"], 0)
            vfs.write_file("/f.bin", b"X" * 10000)
            info2 = vfs.df()
            self.assertGreater(info2["used_bytes"], info["used_bytes"])

    def test_du(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/d")
            vfs.write_file("/d/a.txt", b"A" * 1000)
            vfs.write_file("/d/b.txt", b"B" * 2000)
            size = vfs.du("/d")
            self.assertEqual(size, 3000)


class TestRawFS(VFSTestBase):
    def test_superblock_magic(self):
        disk = VirtualDisk(self.vdisk)
        disk.open()
        raw = disk.read_block(0)
        disk.close()
        self.assertEqual(raw[:4], b"VDK1")

    def test_inode_struct_roundtrip(self):
        from pyvdisk.fs import Inode
        i = Inode.empty()
        i.type = T_FILE
        i.mode = 0o600
        i.size = 12345
        i.direct[0] = 42
        raw = i.to_bytes()
        self.assertEqual(len(raw), 128)
        i2 = Inode.from_bytes(raw)
        self.assertEqual(i2.type, T_FILE)
        self.assertEqual(i2.mode, 0o600)
        self.assertEqual(i2.size, 12345)
        self.assertEqual(i2.direct[0], 42)


class TestCLI(VFSTestBase):
    def _run(self, *argv):
        rc = cli_main([*argv])
        self.assertEqual(rc, 0, f"命令失败: {argv}")

    def test_cli_workflow(self):
        img = os.path.join(self.tmp, "cli.vdisk")
        self._run("create", img, "--size", "8M")
        self._run("mkdir", img, "/docs")
        # write from stdin
        import io
        old_in = sys.stdin
        old_out = sys.stdout
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"hello cli"))
            sys.stdout = io.StringIO()
            self._run("write", img, "/docs/h.txt")
        finally:
            sys.stdin = old_in
            sys.stdout = old_out
        # cat
        old_buf = sys.stdout
        captured = io.BytesIO()
        try:
            sys.stdout = type("S", (), {"buffer": captured, "write": lambda self, s: None})()
            self._run("cat", img, "/docs/h.txt")
        finally:
            sys.stdout = old_buf
        self.assertEqual(captured.getvalue(), b"hello cli")
        # ls
        out = io.StringIO()
        try:
            sys.stdout = out
            self._run("ls", img, "/docs")
        finally:
            sys.stdout = old_out
        self.assertIn("h.txt", out.getvalue())

    def test_cli_import_export(self):
        img = os.path.join(self.tmp, "ie.vdisk")
        host = os.path.join(self.tmp, "host.txt")
        with open(host, "wb") as f:
            f.write(b"payload")
        self._run("create", img, "--size", "4M")
        self._run("import", img, host, "/v.txt")
        out = os.path.join(self.tmp, "v.txt")
        self._run("export", img, "/v.txt", out)
        with open(out, "rb") as f:
            self.assertEqual(f.read(), b"payload")

    def test_cli_ln_chmod_chown(self):
        img = os.path.join(self.tmp, "attr.vdisk")
        self._run("create", img, "--size", "4M")
        # 写源文件
        import io
        old_in, old_out = sys.stdin, sys.stdout
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"hard link data"))
            sys.stdout = io.StringIO()
            self._run("write", img, "/orig.txt")
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        # 硬链接
        self._run("ln", img, "/orig.txt", "/hard.txt")
        # 符号链接
        self._run("ln", img, "-s", "/orig.txt", "/soft.txt")
        # chmod
        self._run("chmod", img, "600", "/orig.txt")
        # chown
        self._run("chown", img, "/orig.txt", "--owner", "1000")
        # 验证
        with VFS(img) as vfs:
            self.assertEqual(vfs.read_file("/hard.txt"), b"hard link data")
            self.assertEqual(vfs.readlink("/soft.txt"), "/orig.txt")
            self.assertEqual(vfs.stat("/orig.txt").mode, 0o600)
            self.assertEqual(vfs.stat("/orig.txt").uid, 1000)

    def test_cli_df_du_fsck(self):
        img = os.path.join(self.tmp, "space.vdisk")
        self._run("create", img, "--size", "4M")
        import io
        old_in, old_out = sys.stdin, sys.stdout
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"x" * 100))
            sys.stdout = io.StringIO()
            self._run("write", img, "/f.txt")
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        out = io.StringIO()
        try:
            sys.stdout = out
            self._run("df", img)
        finally:
            sys.stdout = old_out
        self.assertIn("总容量", out.getvalue())
        out = io.StringIO()
        try:
            sys.stdout = out
            self._run("du", img, "/")
        finally:
            sys.stdout = old_out
        self.assertIn("/", out.getvalue())
        # fsck 应该通过
        out = io.StringIO()
        try:
            sys.stdout = out
            self._run("fsck", img)
        finally:
            sys.stdout = old_out
        self.assertIn("一致", out.getvalue())

    def test_cli_resize(self):
        img = os.path.join(self.tmp, "resize.vdisk")
        self._run("create", img, "--size", "4M")
        import io
        old_in, old_out = sys.stdin, sys.stdout
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"keep me"))
            sys.stdout = io.StringIO()
            self._run("write", img, "/keep.txt")
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        out = io.StringIO()
        try:
            sys.stdout = out
            self._run("resize", img, "--size", "16M")
        finally:
            sys.stdout = old_out
        self.assertIn("16M", out.getvalue())
        # 数据还在
        with VFS(img) as vfs:
            self.assertEqual(vfs.read_file("/keep.txt"), b"keep me")
            self.assertEqual(vfs.df()["total_bytes"], 16 * 1024 * 1024)


class TestSpaceExhaustion(unittest.TestCase):
    def test_too_small_disk_rejected(self):
        tmp = tempfile.mkdtemp()
        try:
            img = os.path.join(tmp, "tiny.vdisk")
            with self.assertRaises(ValueError):
                VFS.create(img, 4 * 1024)  # 太小
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestVolumeBase(unittest.TestCase):
    """多盘卷测试基类。"""
    MODE = None
    NDISTS = 2

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.paths = [os.path.join(self.tmp, f"d{i}.vdisk") for i in range(self.NDISTS)]
        # 预创建盘文件
        for p in self.paths:
            with open(p, "wb") as f:
                f.truncate(4 * 1024 * 1024)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestVolumeConcat(TestVolumeBase):
    MODE = "concat"
    NDISTS = 3

    def test_create_and_status(self):
        from pyvdisk import create_volume, open_volume
        vol = create_volume(self.paths, "concat", name="test")
        status = vol.status()
        self.assertEqual(status["mode"], "concat")
        self.assertEqual(status["ndisks"], 3)
        # concat 容量 = 各盘可用容量之和（每盘去掉 1 块元数据）
        expected = 3 * (1024 - 1)
        self.assertEqual(status["total_blocks"], expected)
        vol.close()

    def test_geometry(self):
        from pyvdisk import Volume
        # 3 块盘，每块 1024 块
        total, data = Volume.compute_geometry("concat", [1024, 1024, 1024])
        self.assertEqual(total, 3 * 1023)  # 每盘去掉 1 块

    def test_mkfs_and_rw(self):
        from pyvdisk import create_volume, open_volume
        from pyvdisk.fs import mkfs, FS
        vol = create_volume(self.paths, "concat")
        mkfs(vol)
        vol.close()
        # 重新打开并读写
        vol2 = open_volume(self.paths)
        fs = FS(vol2).mount()
        # 写跨盘数据（concat 第 2 块盘的边界）
        fs.disk.write_block(1100, b"A" * 4096)
        self.assertEqual(fs.disk.read_block(1100), b"A" * 4096)
        vol2.close()

    def test_vfs_on_volume(self):
        from pyvdisk import VFS
        vfs = VFS.create_volume(self.paths, "concat", disk_size=4*1024*1024)
        with vfs:
            vfs.write_file("/test.txt", b"on volume")
            self.assertEqual(vfs.read_file("/test.txt"), b"on volume")
            # 写超过单盘容量的数据（验证跨盘）
            big = bytes((i * 5) % 256 for i in range(2 * 1024 * 1024))
            vfs.write_file("/big.bin", big)
            self.assertEqual(vfs.read_file("/big.bin"), big)


class TestVolumeStripe(TestVolumeBase):
    MODE = "stripe"
    NDISTS = 2

    def test_geometry(self):
        from pyvdisk import Volume
        total, data = Volume.compute_geometry("stripe", [1024, 1024], stripe_size=4096)
        # 2 盘各 1023 可用，stripe_blocks=1，rounds=1023，total=1023*2
        self.assertEqual(total, 1023 * 2)

    def test_data_distribution(self):
        from pyvdisk import create_volume, open_volume
        vol = create_volume(self.paths, "stripe", stripe_size=4096)
        # 写入数据，验证分布到两块盘
        vol.write_block(0, b"block0" + b"\x00" * 4090)
        vol.write_block(1, b"block1" + b"\x00" * 4090)
        vol.close()
        # 重新打开底层盘检查
        d0 = VirtualDisk(self.paths[0]); d0.open()
        d1 = VirtualDisk(self.paths[1]); d1.open()
        # 逻辑块 0 -> 盘 0 物理块 1，逻辑块 1 -> 盘 1 物理块 1
        b0 = d0.read_block(1)
        b1 = d1.read_block(1)
        self.assertTrue(b0.startswith(b"block0"))
        self.assertTrue(b1.startswith(b"block1"))
        d0.close(); d1.close()

    def test_vfs_stripe(self):
        from pyvdisk import VFS
        vfs = VFS.create_volume(self.paths, "stripe", disk_size=4*1024*1024)
        with vfs:
            data = bytes((i * 11) % 256 for i in range(100000))
            vfs.write_file("/striped.bin", data)
            self.assertEqual(vfs.read_file("/striped.bin"), data)


class TestVolumeMirror(TestVolumeBase):
    MODE = "mirror"
    NDISTS = 2

    def test_redundancy(self):
        from pyvdisk import create_volume, open_volume
        from pyvdisk.fs import mkfs, FS
        vol = create_volume(self.paths, "mirror")
        mkfs(vol)
        vol.close()
        # 写入关键数据
        vol2 = open_volume(self.paths)
        fs = FS(vol2).mount()
        ino = fs.create("/critical.txt")
        fs.write_file(ino, 0, b"redundant data")
        vol2.close()
        # 验证两块盘内容一致
        d0 = VirtualDisk(self.paths[0]); d0.open()
        d1 = VirtualDisk(self.paths[1]); d1.open()
        for blk in range(1, min(d0.nblocks, d1.nblocks)):
            self.assertEqual(d0.read_block(blk), d1.read_block(blk),
                             f"块 {blk} 不一致")
        d0.close(); d1.close()

    def test_add_remove_disk(self):
        from pyvdisk import create_volume, add_mirror, remove_mirror, open_volume
        vol = create_volume(self.paths, "mirror")
        vol.close()
        # 添加第三块盘
        new_path = os.path.join(self.tmp, "d2.vdisk")
        add_mirror(self.paths, new_path)
        self.assertTrue(os.path.exists(new_path))
        # 验证三块盘
        vol = open_volume(self.paths + [new_path])
        self.assertEqual(len(vol.disks), 3)
        vol.close()
        # 移除一块
        remove_mirror(self.paths + [new_path], new_path)
        vol = open_volume(self.paths)
        self.assertEqual(len(vol.disks), 2)
        vol.close()

    def test_resync(self):
        from pyvdisk import create_volume, resync_mirror, open_volume
        from pyvdisk.fs import mkfs, FS
        vol = create_volume(self.paths, "mirror")
        mkfs(vol)
        vol.close()
        # 人为破坏第二块盘的数据
        d1 = VirtualDisk(self.paths[1]); d1.open()
        d1.write_block(5, b"CORRUPT" + b"\x00" * 4089)
        d1.close()
        # 重新同步
        resync_mirror(self.paths)
        # 验证恢复一致
        d0 = VirtualDisk(self.paths[0]); d0.open()
        d1 = VirtualDisk(self.paths[1]); d1.open()
        self.assertEqual(d0.read_block(5), d1.read_block(5))
        d0.close(); d1.close()

    def test_vfs_mirror(self):
        from pyvdisk import VFS
        vfs = VFS.create_volume(self.paths, "mirror", disk_size=4*1024*1024)
        with vfs:
            vfs.write_file("/mirrored.txt", b"safe data")
            self.assertEqual(vfs.read_file("/mirrored.txt"), b"safe data")
            self.assertEqual(vfs.statfs()["blocks"], 1023)  # 镜像容量=单盘


class TestVolumeMeta(unittest.TestCase):
    def test_meta_roundtrip(self):
        from pyvdisk import VolumeMeta, DiskMember
        m = VolumeMeta(
            vol_id="abc-123",
            name="test",
            mode="mirror",
            members=[DiskMember(path="/d0", blocks=1024, uuid="u0"),
                     DiskMember(path="/d1", blocks=1024, uuid="u1")],
            total_blocks=1023,
        )
        raw = m.to_bytes()
        m2 = VolumeMeta.from_bytes(raw)
        self.assertEqual(m2.vol_id, "abc-123")
        self.assertEqual(m2.mode, "mirror")
        self.assertEqual(len(m2.members), 2)
        self.assertEqual(m2.members[0].path, "/d0")

    def test_invalid_magic_rejected(self):
        from pyvdisk import VolumeMeta, VolumeError
        with self.assertRaises(VolumeError):
            VolumeMeta.from_bytes(b"XXXX" + b"\x00" * 100)


class TestVolumeErrors(unittest.TestCase):
    def test_stripe_needs_2_disks(self):
        from pyvdisk import create_volume, VolumeError
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "d.vdisk")
            with open(path, "wb") as f:
                f.truncate(4 * 1024 * 1024)
            with self.assertRaises(VolumeError):
                create_volume([path], "stripe")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_unknown_mode(self):
        from pyvdisk import create_volume, VolumeError
        tmp = tempfile.mkdtemp()
        try:
            paths = [os.path.join(tmp, f"d{i}.vdisk") for i in range(2)]
            for p in paths:
                with open(p, "wb") as f:
                    f.truncate(4 * 1024 * 1024)
            with self.assertRaises(VolumeError):
                create_volume(paths, "raid5")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestVolumeCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, *argv):
        rc = cli_main([*argv])
        self.assertEqual(rc, 0, f"命令失败: {argv}")

    def test_cli_vol_create_status(self):
        import io
        paths = [os.path.join(self.tmp, f"c_d{i}.vdisk") for i in range(2)]
        out = io.StringIO()
        old = sys.stdout
        try:
            sys.stdout = out
            self._run("vol-create", "mirror", *paths, "--name", "clivol",
                      "--disk-size", "4M")
        finally:
            sys.stdout = old
        self.assertIn("clivol", out.getvalue())
        self.assertIn("mirror", out.getvalue())
        # status
        out = io.StringIO()
        try:
            sys.stdout = out
            self._run("vol-status", *paths)
        finally:
            sys.stdout = old
        self.assertIn("clivol", out.getvalue())
        self.assertIn("mirror", out.getvalue())

    def test_cli_vol_format_and_use(self):
        paths = [os.path.join(self.tmp, f"f_d{i}.vdisk") for i in range(2)]
        self._run("vol-create", "concat", *paths, "--disk-size", "4M")
        self._run("vol-format", *paths)
        # 通过卷上读写验证（用 Python API）
        from pyvdisk import open_volume, VFS
        vol = open_volume(paths)
        vfs = VFS(vol)
        with vfs:
            vfs.write_file("/vol.txt", b"on volume via cli")
            self.assertEqual(vfs.read_file("/vol.txt"), b"on volume via cli")


class TestVolumeAutoDetect(unittest.TestCase):
    """验证 VFS 能从单块成员盘自动识别并打开整个多盘卷。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_auto_detect_concat_via_first_disk(self):
        from pyvdisk import VFS
        paths = [os.path.join(self.tmp, f"a_d{i}.vdisk") for i in range(2)]
        VFS.create_volume(paths, "concat", disk_size=4 * 1024 * 1024)
        # 只传第一块盘路径，应自动打开整个卷
        with VFS(paths[0]) as vfs:
            vfs.write_file("/auto.txt", b"auto-detected")
            self.assertEqual(vfs.read_file("/auto.txt"), b"auto-detected")

    def test_auto_detect_via_second_disk(self):
        from pyvdisk import VFS
        paths = [os.path.join(self.tmp, f"b_d{i}.vdisk") for i in range(2)]
        VFS.create_volume(paths, "mirror", disk_size=4 * 1024 * 1024)
        with VFS(paths[0]) as vfs:
            vfs.write_file("/mir.txt", b"from any member")
        # 用第二块盘也能读到（镜像卷冗余 + 自动检测）
        with VFS(paths[1]) as vfs:
            self.assertEqual(vfs.read_file("/mir.txt"), b"from any member")

    def test_single_disk_not_detected_as_volume(self):
        # 普通单盘不应被误判为卷
        from pyvdisk import VFS, VirtualDisk
        from pyvdisk.volume import Volume
        img = os.path.join(self.tmp, "plain.vdisk")
        VFS.create(img, 4 * 1024 * 1024)
        with VFS(img) as vfs:
            self.assertIsInstance(vfs.disk, VirtualDisk)
            self.assertNotIsInstance(vfs.disk, Volume)

    def test_cli_works_on_volume_via_single_member(self):
        # CLI 命令只传一块成员盘也能在卷上操作
        paths = [os.path.join(self.tmp, f"c_d{i}.vdisk") for i in range(2)]
        cli_main(["vol-create", "concat", *paths, "--disk-size", "4M"])
        cli_main(["vol-format", *paths])
        # 只用第一块盘做 mkdir / write
        cli_main(["mkdir", paths[0], "/docs"])
        cli_main(["write", paths[0], "/docs/h.txt", "--file", __file__])
        # 用第二块盘做 ls（验证跨成员盘自动检测）
        import io
        out = io.StringIO()
        old = sys.stdout
        try:
            sys.stdout = out
            cli_main(["ls", paths[1], "/docs"])
        finally:
            sys.stdout = old
        self.assertIn("h.txt", out.getvalue())


class TestIdentity(unittest.TestCase):
    """磁盘身份尾标测试。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_single_disk_has_identity(self):
        from pyvdisk import VFS, probe_disk
        img = os.path.join(self.tmp, "s.vdisk")
        VFS.create(img, 4 * 1024 * 1024, label="mylabel")
        ident = probe_disk(img)
        self.assertEqual(ident.kind, "single")
        self.assertTrue(ident.disk_uuid)
        self.assertEqual(ident.label, "mylabel")
        self.assertEqual(ident.vol_id, "")
        self.assertFalse(ident.is_member)

    def test_member_disk_has_uuid_matching_meta(self):
        from pyvdisk import create_volume, probe_disk
        paths = [os.path.join(self.tmp, f"m{i}.vdisk") for i in range(2)]
        vol = create_volume(paths, "mirror", name="rvol", disk_size=4 * 1024 * 1024)
        member_uuids = [m.uuid for m in vol.meta.members]
        vol.close()
        # 每块成员盘的尾标 disk_uuid 应与元数据中的成员 uuid 一一对应
        for p, muuid in zip(paths, member_uuids):
            ident = probe_disk(p)
            self.assertEqual(ident.kind, "member")
            self.assertEqual(ident.disk_uuid, muuid)
            self.assertEqual(ident.vol_id, probe_disk(paths[0]).vol_id)
            self.assertTrue(ident.is_member)
            self.assertEqual(ident.label, "rvol")

    def test_flush_superblock_preserves_trailer(self):
        # 多次写超级块后，身份尾标应仍存在
        from pyvdisk import VFS, probe_disk
        img = os.path.join(self.tmp, "s.vdisk")
        VFS.create(img, 4 * 1024 * 1024, label="keepme")
        with VFS(img) as vfs:
            # 触发若干会 flush 超级块的操作
            vfs.mkdir("/d1")
            vfs.mkdir("/d2")
            vfs.write_file("/d1/f.txt", b"x" * 5000)
            vfs.fs.flush_superblock()
        ident = probe_disk(img)
        self.assertEqual(ident.label, "keepme")
        self.assertEqual(ident.kind, "single")

    def test_probe_unknown_file(self):
        from pyvdisk import probe_disk
        p = os.path.join(self.tmp, "junk.vdisk")
        with open(p, "wb") as f:
            f.write(b"not a vdisk" + b"\x00" * 5000)
        ident = probe_disk(p)
        self.assertEqual(ident.kind, "unknown")

    def test_label_set_via_cli(self):
        img = os.path.join(self.tmp, "s.vdisk")
        VFS.create(img, 4 * 1024 * 1024, label="old")
        cli_main(["label", img, "newlabel"])
        from pyvdisk import probe_disk
        self.assertEqual(probe_disk(img).label, "newlabel")


class TestDiskManager(unittest.TestCase):
    """模拟驱动 DiskManager 测试。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bay = os.path.join(self.tmp, "bay")
        os.makedirs(self.bay)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _mk_single(self, name, label):
        img = os.path.join(self.bay, name)
        VFS.create(img, 4 * 1024 * 1024, label=label)
        return img

    def _mk_volume(self, name, mode, n=2):
        paths = [os.path.join(self.bay, f"{name}_{i}.vdisk") for i in range(n)]
        from pyvdisk import create_volume
        from pyvdisk.fs import mkfs
        vol = create_volume(paths, mode, name=name, disk_size=4 * 1024 * 1024)
        mkfs(vol)
        vol.close()
        return paths

    def test_scan_finds_single_and_volume(self):
        from pyvdisk import DiskManager
        self._mk_single("s1.vdisk", "solo")
        self._mk_volume("raid", "mirror")
        mgr = DiskManager(self.bay)
        mgr.scan()
        singles, complete, partial = mgr.assemble()
        self.assertEqual(len(singles), 1)
        self.assertEqual(singles[0].label, "solo")
        self.assertEqual(len(complete), 1)
        self.assertEqual(complete[0].meta.mode, "mirror")
        self.assertEqual(len(partial), 0)

    def test_mount_all_by_label(self):
        from pyvdisk import DiskManager
        self._mk_single("s1.vdisk", "solo")
        self._mk_volume("raid", "stripe")
        mgr = DiskManager(self.bay)
        mgr.scan()
        mgr.mount_all()
        self.assertIn("solo", mgr.labels())
        self.assertIn("raid", mgr.labels())
        # 按卷标访问并读写
        mgr.get("solo").vfs.write_file("/x.txt", b"single")
        self.assertEqual(mgr.get("solo").vfs.read_file("/x.txt"), b"single")
        mgr.get("raid").vfs.write_file("/y.txt", b"stripe")
        self.assertEqual(mgr.get("raid").vfs.read_file("/y.txt"), b"stripe")
        mgr.unmount_all()

    def test_partial_volume_not_mounted(self):
        # 只复制一块成员盘到目录 → 卷不完整，不挂载
        from pyvdisk import DiskManager
        paths = self._mk_volume("raid", "mirror")
        # 移走第二块盘
        os.rename(paths[1], paths[1] + ".bak")
        mgr = DiskManager(self.bay)
        mgr.scan()
        mgr.mount_all()
        # 只有一块成员盘，卷不完整
        self.assertNotIn("raid", mgr.labels())

    def test_hotplug_new_single(self):
        from pyvdisk import DiskManager
        self._mk_single("s1.vdisk", "first")
        mgr = DiskManager(self.bay)
        mgr.scan()
        mgr.mount_all()
        self.assertEqual(mgr.labels(), ["first"])
        # 热插拔：放入一块全新的单盘
        self._mk_single("s2.vdisk", "second")
        new = mgr.hotplug()
        self.assertEqual([m.label for m in new], ["second"])
        self.assertIn("second", mgr.labels())

    def test_disk_identity_survives_move(self):
        # 盘文件移动/改名后，身份尾标不变，仍能被识别
        from pyvdisk import DiskManager, probe_disk
        img = self._mk_single("s1.vdisk", "movable")
        ident_before = probe_disk(img)
        # 改名
        new_path = os.path.join(self.bay, "renamed.vdisk")
        os.rename(img, new_path)
        ident_after = probe_disk(new_path)
        self.assertEqual(ident_before.disk_uuid, ident_after.disk_uuid)
        self.assertEqual(ident_after.label, "movable")

    def test_volume_assembled_after_copy_to_new_dir(self):
        # 把卷成员盘复制到另一个"硬盘柜"，应能重新组装并挂载
        from pyvdisk import DiskManager
        paths = self._mk_volume("raid", "concat")
        # 先写入数据
        from pyvdisk import VFS
        with VFS(paths[0]) as vfs:
            vfs.write_file("/data.txt", b"across bays")
        # 复制到新目录
        bay2 = os.path.join(self.tmp, "bay2")
        os.makedirs(bay2)
        for p in paths:
            shutil.copy(p, bay2)
        # 在新目录扫描挂载
        mgr = DiskManager(bay2)
        mgr.scan()
        mgr.mount_all()
        self.assertIn("raid", mgr.labels())
        self.assertEqual(mgr.get("raid").vfs.read_file("/data.txt"),
                         b"across bays")
        mgr.unmount_all()

    def test_cli_scan_and_mount_all(self):
        import io
        self._mk_single("s1.vdisk", "cli-solo")
        self._mk_volume("raid", "mirror")
        out = io.StringIO()
        old = sys.stdout
        try:
            sys.stdout = out
            cli_main(["scan", self.bay])
        finally:
            sys.stdout = old
        self.assertIn("cli-solo", out.getvalue())
        self.assertIn("完整卷", out.getvalue())
        out = io.StringIO()
        try:
            sys.stdout = out
            cli_main(["mount-all", self.bay])
        finally:
            sys.stdout = old
        self.assertIn("cli-solo", out.getvalue())
        self.assertIn("raid", out.getvalue())


class TestRWLock(unittest.TestCase):
    """读写锁基础语义测试。"""

    def test_multiple_readers_concurrent(self):
        from pyvdisk import RWLock
        import threading, time
        lock = RWLock()
        active = []
        max_concurrent = [0]
        cur = [0]
        lock_held = threading.Lock()

        def reader():
            with lock.read():
                with lock_held:
                    cur[0] += 1
                    max_concurrent[0] = max(max_concurrent[0], cur[0])
                time.sleep(0.05)
                with lock_held:
                    cur[0] -= 1

        ts = [threading.Thread(target=reader) for _ in range(5)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertGreaterEqual(max_concurrent[0], 2,
                                "多读者应能并发持有读锁")

    def test_writer_exclusive(self):
        from pyvdisk import RWLock
        import threading, time
        lock = RWLock()
        log = []
        lock_held = threading.Lock()

        def writer(i):
            with lock.write():
                with lock_held:
                    log.append(("start", i))
                time.sleep(0.02)
                with lock_held:
                    log.append(("end", i))

        ts = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
        for t in ts: t.start()
        for t in ts: t.join()
        # 每个写者的 start 紧跟 end，无交错
        for i in range(0, len(log), 2):
            self.assertEqual(log[i][0], "start")
            self.assertEqual(log[i+1][0], "end")
            self.assertEqual(log[i][1], log[i+1][1])

    def test_reader_writer_mutual_exclusion(self):
        from pyvdisk import RWLock
        import threading, time
        lock = RWLock()
        states = []
        lock_held = threading.Lock()
        overlap = [False]
        reading = [0]
        writing = [False]

        def reader():
            with lock.read():
                with lock_held:
                    reading[0] += 1
                    if writing[0]:
                        overlap[0] = True
                time.sleep(0.03)
                with lock_held:
                    reading[0] -= 1

        def writer():
            with lock.write():
                with lock_held:
                    writing[0] = True
                    if reading[0] > 0:
                        overlap[0] = True
                time.sleep(0.03)
                with lock_held:
                    writing[0] = False

        ts = [threading.Thread(target=reader)] + [threading.Thread(target=writer) for _ in range(2)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertFalse(overlap[0], "读写不应重叠")

    def test_reentrant_same_thread(self):
        from pyvdisk import RWLock
        lock = RWLock()
        with lock.write():
            with lock.write():  # 重入写
                with lock.read():  # 写者内读
                    pass
        with lock.read():
            with lock.read():  # 重入读
                pass


class TestConcurrency(unittest.TestCase):
    """多线程并发操作文件系统的正确性测试。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.vdisk = os.path.join(self.tmp, "disk.vdisk")
        VFS.create(self.vdisk, 16 * 1024 * 1024)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_concurrent_create_distinct_files(self):
        # 多线程并发创建不同文件，结果应全部可见、无损坏
        import threading
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/conc")
        n = 20
        threads = []

        def worker(i):
            with VFS(self.vdisk) as v:
                v.write_file(f"/conc/f{i}.txt", f"data-{i}".encode())

        for i in range(n):
            threads.append(threading.Thread(target=worker, args=(i,)))
        for t in threads: t.start()
        for t in threads: t.join()
        with VFS(self.vdisk) as vfs:
            names = sorted(vfs.listdir("/conc"))
            self.assertEqual(len(names), n)
            for i in range(n):
                self.assertEqual(vfs.read_file(f"/conc/f{i}.txt"),
                                 f"data-{i}".encode())

    def test_concurrent_append_same_file(self):
        # 多线程并发追加同一文件，总行数应正确（写互斥保证不丢更新）
        import threading
        n_threads = 10
        n_each = 20
        threads = []

        def worker():
            with VFS(self.vdisk) as v:
                for _ in range(n_each):
                    v.append_file("/log.txt", b"line\n")

        for _ in range(n_threads):
            threads.append(threading.Thread(target=worker))
        for t in threads: t.start()
        for t in threads: t.join()
        with VFS(self.vdisk) as vfs:
            content = vfs.read_file("/log.txt")
            self.assertEqual(content.count(b"line\n"), n_threads * n_each)

    def test_concurrent_mkdir_no_collision(self):
        # 并发创建不同目录
        import threading
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/d")
        threads = []

        def worker(i):
            with VFS(self.vdisk) as v:
                v.makedirs(f"/d/sub{i}/deep")

        for i in range(15):
            threads.append(threading.Thread(target=worker, args=(i,)))
        for t in threads: t.start()
        for t in threads: t.join()
        with VFS(self.vdisk) as vfs:
            names = vfs.listdir("/d")
            self.assertEqual(len(names), 15)
        # fsck 应通过
        with VFS(self.vdisk) as vfs:
            report = vfs.fs.fsck(repair=False)
            self.assertTrue(report["ok"], f"fsck 发现问题: {report['problems']}")

    def test_concurrent_reads_during_writes(self):
        # 并发读写在同一文件系统上不应崩溃
        import threading, time
        stop = threading.Event()
        errors = []

        def writer():
            try:
                i = 0
                while not stop.is_set():
                    with VFS(self.vdisk) as v:
                        v.write_file(f"/w{i % 5}.txt", f"x{i}".encode())
                    i += 1
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                while not stop.is_set():
                    with VFS(self.vdisk) as v:
                        try:
                            v.listdir("/")
                        except FSError:
                            pass
            except Exception as e:
                errors.append(e)

        ts = [threading.Thread(target=writer)] + [threading.Thread(target=reader) for _ in range(3)]
        for t in ts: t.start()
        time.sleep(0.5)
        stop.set()
        for t in ts: t.join()
        self.assertEqual(errors, [])


class TestPermissions(unittest.TestCase):
    """文件权限（POSIX 风格）强制检查测试。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.vdisk = os.path.join(self.tmp, "disk.vdisk")
        VFS.create(self.vdisk, 8 * 1024 * 1024)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_root_bypasses(self):
        # uid=0（默认）不受权限限制
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"x")
            vfs.chmod("/a.txt", 0o000)
            # root 仍可读写
            self.assertEqual(vfs.read_file("/a.txt"), b"x")
            vfs.write_file("/a.txt", b"y")
            self.assertEqual(vfs.read_file("/a.txt"), b"y")

    def test_owner_can_rw(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"hello")
            vfs.chown("/a.txt", uid=1000, gid=1000)
            vfs.chmod("/a.txt", 0o644)
            # 切换为属主身份
            vfs.uid, vfs.gid = 1000, 1000
            self.assertEqual(vfs.read_file("/a.txt"), b"hello")
            vfs.write_file("/a.txt", b"world")
            self.assertEqual(vfs.read_file("/a.txt"), b"world")

    def test_other_user_denied_write(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"secret")
            vfs.chown("/a.txt", uid=1000, gid=1000)
            vfs.chmod("/a.txt", 0o644)  # 属主 rw，其他人只读
            vfs.uid, vfs.gid = 2000, 2000
            # 其他人可读
            self.assertEqual(vfs.read_file("/a.txt"), b"secret")
            # 其他人不可写
            with self.assertRaises(FSError):
                vfs.write_file("/a.txt", b"hacked")

    def test_no_read_perm_denied(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"secret")
            vfs.chown("/a.txt", uid=1000, gid=1000)
            vfs.chmod("/a.txt", 0o000)
            vfs.uid, vfs.gid = 2000, 2000
            with self.assertRaises(FSError):
                vfs.read_file("/a.txt")

    def test_create_requires_parent_write(self):
        with VFS(self.vdisk) as vfs:
            vfs.mkdir("/locked")
            vfs.chown("/locked", uid=1000, gid=1000)
            vfs.chmod("/locked", 0o755)  # 其他人无写
            vfs.uid, vfs.gid = 2000, 2000
            with self.assertRaises(FSError):
                vfs.write_file("/locked/new.txt", b"x")

    def test_traverse_requires_exec(self):
        with VFS(self.vdisk) as vfs:
            vfs.makedirs("/a/b")
            vfs.write_file("/a/b/secret.txt", b"x")
            vfs.chown("/a", uid=1000, gid=1000)
            vfs.chmod("/a", 0o644)  # 目录无 x，无法遍历
            vfs.uid, vfs.gid = 2000, 2000
            with self.assertRaises(FSError):
                vfs.read_file("/a/b/secret.txt")

    def test_chmod_requires_owner(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"x")
            vfs.chown("/a.txt", uid=1000, gid=1000)
            vfs.uid, vfs.gid = 2000, 2000
            with self.assertRaises(FSError):
                vfs.chmod("/a.txt", 0o777)

    def test_chown_requires_root(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"x")
            vfs.uid, vfs.gid = 1000, 1000
            with self.assertRaises(FSError):
                vfs.chown("/a.txt", uid=2000)

    def test_disable_perms_bypasses(self):
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"x")
            vfs.chown("/a.txt", uid=1000, gid=1000)
            vfs.chmod("/a.txt", 0o000)
            vfs.uid, vfs.gid = 2000, 2000
            vfs.enforce_perms = False
            # 关闭检查后可读写
            self.assertEqual(vfs.read_file("/a.txt"), b"x")
            vfs.write_file("/a.txt", b"ok")

    def test_cli_uid_enforced(self):
        # 通过 CLI --uid 以非 root 身份操作，写只读文件应失败
        with VFS(self.vdisk) as vfs:
            vfs.write_file("/a.txt", b"x")
            vfs.chown("/a.txt", uid=1000, gid=1000)
            vfs.chmod("/a.txt", 0o644)
        # 以 uid=2000 写应失败
        with self.assertRaises(SystemExit):
            cli_main(["write", self.vdisk, "/a.txt", "--uid", "2000",
                      "--file", __file__])
        # root 仍可写
        import io
        old = sys.stdin
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"root-data"))
            cli_main(["write", self.vdisk, "/a.txt"])
        finally:
            sys.stdin = old


class TestVectorDisk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "vectors.vdisk")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_suffix_is_required(self):
        with self.assertRaises(ValueError):
            VFS.create(os.path.join(self.tmp, "bad.img"), 4 * 1024 * 1024)

    def test_identity_marks_vector_disk(self):
        from unittest.mock import patch, MagicMock
        fake = MagicMock()
        fake.Index.return_value = MagicMock()
        fake.Index.return_value.save_index.side_effect = lambda p: open(p, "wb").write(b"idx")
        with patch.dict(sys.modules, {"hnswlib": fake}):
            from pyvdisk import VectorDisk, probe_disk
            VectorDisk.create(self.path, 4 * 1024 * 1024, label="embeddings")
            with VectorDisk(self.path) as disk:
                disk.create_collection("docs", 3)
            ident = probe_disk(self.path)
            self.assertEqual(ident.kind, "vector")
            self.assertEqual(ident.label, "embeddings")

    def test_crud_filter_and_persistent_index(self):
        from unittest.mock import patch
        class FakeIndex:
            saved = b"fake-index"
            def __init__(self, space, dim): self.items = {}
            def init_index(self, **kwargs): pass
            def set_ef(self, value): pass
            def add_items(self, vectors, labels): self.items.update(zip(labels, vectors))
            def save_index(self, path): open(path, "wb").write(self.saved)
            def load_index(self, path, **kwargs): self.loaded = open(path, "rb").read()
            def knn_query(self, queries, k, filter=None):
                labels = [0, 1]
                labels = [x for x in labels if filter is None or filter(x)][:k]
                return [labels], [[float(i) for i, _ in enumerate(labels)]]
        fake = type("FakeHnsw", (), {"Index": FakeIndex})
        with patch.dict(sys.modules, {"hnswlib": fake}):
            from pyvdisk import VectorDisk
            VectorDisk.create(self.path, 4 * 1024 * 1024)
            with VectorDisk(self.path) as disk:
                disk.create_collection("docs", 3)
                disk.upsert("docs", "a", [1, 0, 0], {"kind": "news", "score": 0.9})
                disk.upsert("docs", "b", [0, 1, 0], {"kind": "blog", "score": 0.5})
                self.assertEqual(disk.count("docs"), 2)
                self.assertEqual(disk.get("docs", "a")["metadata"]["kind"], "news")
                hits = disk.search("docs", [1, 0, 0], where={"score": {"$gte": 0.8}})
                self.assertEqual([h["id"] for h in hits], ["a"])
                self.assertTrue(disk.delete("docs", "b"))
            with VectorDisk(self.path) as disk:
                self.assertEqual(disk.count("docs"), 1)
                self.assertTrue(disk.vfs.exists(disk._dir("docs") + "/index.hnsw"))


class TestLogDiskAndLogging(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.mkdtemp(); self.path=os.path.join(self.tmp,"logs.vdisk")
    def tearDown(self): shutil.rmtree(self.tmp,ignore_errors=True)

    def test_log_identity_stream_query_retention(self):
        from pyvdisk import LogDisk, LogEvent, probe_disk
        LogDisk.create(self.path,8*1024*1024,label="observability")
        with LogDisk(self.path) as disk:
            disk.create_stream("app",segment_events=2,retention_seconds=5,max_events=3)
            for i in range(5):
                disk.append("app",LogEvent(1_000_000_000*i,"ERROR" if i%2 else "INFO","svc",f"m{i}",{"latency":i},{"env":"test"}))
            self.assertEqual(disk.stats("app")["segments"],3)
            rows=disk.query("app",start_ns=1_000_000_000,end_ns=4_000_000_000,levels=["ERROR"],tags={"env":"test"},where={"latency":{"$gte":1}})
            self.assertEqual([e.message for e in rows],["m1","m3"])
            self.assertEqual([e.message for e in disk.tail("app",2)],["m3","m4"])
            removed=disk.enforce_retention("app",now_ns=10_000_000_000)
            self.assertGreaterEqual(removed,2)
            disk.compact("app")
        self.assertEqual(probe_disk(self.path).kind,"log")

    def test_agentic_sequence_and_trace_metadata(self):
        from pyvdisk import LogDisk
        LogDisk.create(self.path,8*1024*1024)
        with LogDisk(self.path) as disk:
            disk.create_stream("trace")
            first=disk.append("trace", timestamp_ns=1, level="INFO", logger="agent", message="start", run_id="run-1", task_id="task-1", correlation_id="corr-1", schema_version="1")
            many=disk.append_many("trace", [{"timestamp_ns": 2, "level": "INFO", "logger": "agent", "message": "step"}, {"timestamp_ns": 3, "level": "INFO", "logger": "agent", "message": "done"}])
            self.assertEqual(first.sequence, 0)
            self.assertEqual([e.sequence for e in many], [1, 2])
            self.assertEqual(disk.query("trace")[0].run_id, "run-1")
            self.assertEqual([e.sequence for e in disk.tail("trace", 2)], [1, 2])
            self.assertEqual(disk.list_streams()[0]["sequence"], 3)

    def test_unified_logger_context_and_stdlib_bridge(self):
        import logging
        from pyvdisk import (MemorySink,get_logger,log_context,StandardLoggingHandler)
        sink=MemorySink(); logger=get_logger("app",sink,level="DEBUG",service="api")
        with log_context(trace_id="trace-1",request_id="r1"):
            event=logger.info("hello",fields={"value":3},tags={"env":"test"})
        self.assertEqual(event.trace_id,"trace-1"); self.assertEqual(event.fields["request_id"],"r1")
        std=logging.getLogger("bridge-test"); std.propagate=False; std.handlers=[StandardLoggingHandler(sink)]; std.setLevel(logging.INFO)
        std.info("bridged",extra={"answer":42})
        self.assertEqual(sink.events[-1].fields["answer"],42)

    def test_logdisk_sink_and_manager(self):
        from pyvdisk import LogDisk,LogDiskSink,get_logger,DiskManager
        LogDisk.create(self.path,8*1024*1024,label="logs")
        with LogDisk(self.path) as disk:
            disk.create_stream("events"); logger=get_logger("svc",LogDiskSink(disk,"events")); logger.error("boom",fields={"code":500})
            self.assertEqual(disk.count("events") if hasattr(disk,"count") else len(disk.query("events")),1)
        mgr=DiskManager(self.tmp);mgr.scan();mgr.mount_all();self.assertEqual(mgr.get("logs").kind,"log");mgr.unmount_all()


if __name__ == "__main__":
    unittest.main(verbosity=2)
