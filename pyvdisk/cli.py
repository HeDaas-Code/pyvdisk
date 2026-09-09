"""vdisk 命令行工具。

用法示例：
    python -m pyvdisk create disk.vdisk --size 16M
    python -m pyvdisk ls disk.vdisk /
    python -m pyvdisk mkdir disk.vdisk /docs
    python -m pyvdisk write disk.vdisk /docs/hello.txt <<< "hi"
    python -m pyvdisk cat disk.vdisk /docs/hello.txt
    python -m pyvdisk import disk.vdisk ./localfile.bin /data/file.bin
    python -m pyvdisk mount disk.vdisk /mnt/vdisk   # 需要 fusepy
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from .vfs import VFS
from .fs import FSError, T_DIR, T_FILE, T_SYMLINK


def _parse_size(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("大小不能为空")
    mult = 1
    if s[-1].isdigit():
        return int(s)
    suffix = s[-1].upper()
    if suffix == "K":
        mult, num = 1024, s[:-1]
    elif suffix == "M":
        mult, num = 1024 * 1024, s[:-1]
    elif suffix == "G":
        mult, num = 1024 * 1024 * 1024, s[:-1]
    else:
        num = s
    try:
        return int(num) * mult
    except ValueError:
        raise ValueError(f"无法解析大小: {s}")


def _type_str(t: int) -> str:
    return {T_DIR: "dir", T_FILE: "file", T_SYMLINK: "link"}.get(t, "?")


def _human_size(n: int) -> str:
    for unit in ["B", "K", "M", "G", "T"]:
        if n < 1024:
            return f"{n}{unit}"
        n = int(n / 1024)
    return f"{n}T"


def _add_cred_args(sp):
    """给子命令添加身份/权限相关选项。"""
    sp.add_argument("--uid", type=int, default=0, help="以该 uid 身份操作（0=root 放行权限）")
    sp.add_argument("--gid", type=int, default=0, help="以该 gid 身份操作")
    sp.add_argument("--no-perm", action="store_true", help="关闭权限检查（等同 root）")


def _open_vfs(args):
    """按 args 中的身份/权限设置打开 VFS，返回已挂载的 VFS（需配合 with 使用）。"""
    vfs = VFS(args.image)
    if getattr(args, "no_perm", False):
        vfs.enforce_perms = False
    else:
        vfs.uid = getattr(args, "uid", 0)
        vfs.gid = getattr(args, "gid", 0)
    return vfs


# ---- 子命令实现 ----
def cmd_create(args):
    size = _parse_size(args.size)
    VFS.create(args.image, size, label=args.label or "")
    print(f"已创建虚拟磁盘: {args.image} ({_human_size(size)})"
          + (f" 卷标={args.label}" if args.label else ""))


def cmd_info(args):
    from .disk import VirtualDisk
    from .fs import FS
    import os
    disk = VirtualDisk(args.image)
    disk.open()
    fs = FS(disk).mount()
    sb = fs.sb
    print(f"镜像文件:    {args.image}")
    print(f"文件大小:    {_human_size(os.path.getsize(args.image))}")
    print(f"魔数/版本:   {sb.magic.decode(errors='replace')} v{sb.version}")
    print(f"块大小:      {sb.block_size} 字节")
    print(f"总块数:      {sb.total_blocks}")
    print(f"总 inode:    {sb.total_inodes}")
    print(f"数据块:      {sb.data_blocks} (起始块 {sb.data_start})")
    print(f"根 inode:    {sb.root_inode}")
    # 统计已用
    used_inodes = 0
    for i in range(sb.total_inodes):
        if fs._bitmap_get(sb.inode_bitmap_start, i):
            used_inodes += 1
    used_blocks = 0
    for i in range(sb.total_blocks):
        if fs._bitmap_get(sb.block_bitmap_start, i):
            used_blocks += 1
    print(f"已用 inode:  {used_inodes} / {sb.total_inodes}")
    print(f"已用块:      {used_blocks} / {sb.total_blocks}")
    disk.close()


def cmd_status(args):
    """Read-only status for a canonical DataDisk and persisted runs."""
    import json
    from .infrastructure import DataDisk, RunStateStore
    disk = DataDisk(args.image)
    try:
        disk.mount()
        manifest = disk.manifest()
        print(json.dumps({
            "path": args.image,
            "type": manifest.get("type"),
            "format_version": manifest.get("version"),
            "mounted": disk.mounted,
            "namespaces": manifest.get("namespaces", []),
            "runs": {status: len(RunStateStore.from_data_disk(disk).list(status=status))
                     for status in sorted(RunStateStore.STATES)},
        }, ensure_ascii=False, indent=2))
    finally:
        disk.close()


def cmd_ls(args):
    with _open_vfs(args) as vfs:
        path = args.path or "/"
        try:
            entries = vfs.listdir_with_stat(path)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
        if not args.long:
            for name, _ in entries:
                print(name)
            return
        # long 格式
        print(f"{'type':6} {'size':>10}  {'ino':>6}  name")
        for name, st in entries:
            print(f"{_type_str(st.type):6} {_human_size(st.size):>10}  {st.ino:>6}  {name}")


def cmd_mkdir(args):
    with _open_vfs(args) as vfs:
        try:
            if args.parents:
                vfs.makedirs(args.path)
            else:
                vfs.mkdir(args.path)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_rmdir(args):
    with _open_vfs(args) as vfs:
        try:
            if args.recursive:
                vfs.rmtree(args.path)
            else:
                vfs.rmdir(args.path)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_rm(args):
    with _open_vfs(args) as vfs:
        try:
            if args.recursive and vfs.isdir(args.path):
                vfs.rmtree(args.path)
            else:
                vfs.remove(args.path)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_cat(args):
    with _open_vfs(args) as vfs:
        try:
            data = vfs.read_file(args.path)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    out = sys.stdout.buffer if hasattr(sys.stdout, "buffer") else sys.stdout
    out.write(data)
    out.flush()


def cmd_write(args):
    with _open_vfs(args) as vfs:
        if args.file:
            with open(args.file, "rb") as f:
                data = f.read()
        else:
            data = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode()
        try:
            vfs.write_file(args.path, data)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    print(f"已写入 {len(data)} 字节到 {args.path}")


def cmd_append(args):
    with _open_vfs(args) as vfs:
        if args.file:
            with open(args.file, "rb") as f:
                data = f.read()
        else:
            data = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode()
        vfs.append_file(args.path, data)
    print(f"已追加 {len(data)} 字节到 {args.path}")


def cmd_cp(args):
    with _open_vfs(args) as vfs:
        data = vfs.read_file(args.src)
        vfs.write_file(args.dst, data)
    print(f"已复制 {args.src} -> {args.dst} ({len(data)} 字节)")


def cmd_mv(args):
    with _open_vfs(args) as vfs:
        vfs.rename(args.src, args.dst)


def cmd_import(args):
    with _open_vfs(args) as vfs:
        if args.recursive and os.path.isdir(args.host_path):
            vfs.import_host_tree(args.host_path, args.vpath)
            print(f"已导入目录树 {args.host_path} -> {args.vpath}")
        else:
            vfs.import_host_file(args.host_path, args.vpath)
            print(f"已导入 {args.host_path} -> {args.vpath}")


def cmd_export(args):
    with _open_vfs(args) as vfs:
        vfs.export_to_host(args.vpath, args.host_path)
    print(f"已导出 {args.vpath} -> {args.host_path}")


def cmd_stat(args):
    with _open_vfs(args) as vfs:
        st = vfs.stat(args.path)
    import time as _t
    print(f"  路径:   {args.path}")
    print(f"  inode:  {st.ino}")
    print(f"  类型:   {_type_str(st.type)}")
    print(f"  模式:   {oct(st.mode)}")
    print(f"  大小:   {st.size} 字节")
    print(f"  nlink:  {st.nlink}")
    print(f"  atime:  {_t.strftime('%Y-%m-%d %H:%M:%S', _t.localtime(st.atime))}")
    print(f"  mtime:  {_t.strftime('%Y-%m-%d %H:%M:%S', _t.localtime(st.mtime))}")
    print(f"  ctime:  {_t.strftime('%Y-%m-%d %H:%M:%S', _t.localtime(st.ctime))}")


def cmd_tree(args):
    with _open_vfs(args) as vfs:
        root = args.path or "/"
        for top, dirs, files in vfs.walk(root):
            depth = top.rstrip("/").count("/") - root.rstrip("/").count("/")
            if depth < 0:
                depth = 0
            indent = "  " * depth
            print(f"{indent}{os.path.basename(top) or top}/")
            for f in files:
                print(f"{indent}  {f}")


def cmd_mount(args):
    from .fuse_mount import mount as fuse_mount
    with _open_vfs(args) as vfs:
        print(f"挂载 {args.image} -> {args.mountpoint} (Ctrl+C 卸载)")
        fuse_mount(vfs, args.mountpoint, foreground=True)


def cmd_touch(args):
    with _open_vfs(args) as vfs:
        if not vfs.exists(args.path):
            vfs.write_file(args.path, b"")
        else:
            # 更新时间戳
            from .fs import FS
            fs = vfs._fs_or_raise()
            ino = fs.resolve(args.path)
            inode = fs.read_inode(ino)
            import time as _t
            inode.mtime = int(_t.time())
            inode.atime = int(_t.time())
            fs.write_inode(ino, inode)


def cmd_format(args):
    """在已有空文件上格式化。"""
    from .disk import VirtualDisk
    from .fs import mkfs
    import os as _os
    size = _parse_size(args.size)
    disk = VirtualDisk(args.image)
    disk.create(size)
    try:
        mkfs(disk, label=args.label or "")
    finally:
        disk.close()
    print(f"已格式化: {args.image} ({_human_size(size)})"
          + (f" 卷标={args.label}" if args.label else ""))


def cmd_ln(args):
    with _open_vfs(args) as vfs:
        if args.symlink:
            vfs.symlink(args.target, args.linkpath)
            print(f"符号链接: {args.linkpath} -> {args.target}")
        else:
            vfs.link(args.target, args.linkpath)
            print(f"硬链接: {args.linkpath} => {args.target}")


def cmd_chmod(args):
    with _open_vfs(args) as vfs:
        try:
            mode = int(args.mode, 8)
        except ValueError:
            print(f"无效的权限模式: {args.mode}", file=sys.stderr)
            sys.exit(1)
        try:
            vfs.chmod(args.path, mode)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_chown(args):
    with _open_vfs(args) as vfs:
        uid = int(args.owner) if args.owner is not None else -1
        gid = int(args.group) if args.group is not None else -1
        try:
            vfs.chown(args.path, uid, gid)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_df(args):
    with _open_vfs(args) as vfs:
        info = vfs.df()
        print(f"镜像:        {args.image}")
        print(f"总容量:      {_human_size(info['total_bytes'])}")
        print(f"已用:        {_human_size(info['used_bytes'])}")
        print(f"可用:        {_human_size(info['free_bytes'])}")
        print(f"块大小:      {info['block_size']} 字节")
        print(f"inode 总数:  {info['total_inodes']}")
        print(f"inode 可用:  {info['free_inodes']}")


def cmd_du(args):
    with _open_vfs(args) as vfs:
        path = args.path or "/"
        total = vfs.du(path)
        print(f"{_human_size(total):>10}  {path}")


def cmd_fsck(args):
    with _open_vfs(args) as vfs:
        report = vfs.fsck(repair=args.repair)
        if report["ok"]:
            print("文件系统一致，未发现问题。")
        else:
            print(f"发现 {len(report['problems'])} 个问题:")
            for p in report["problems"]:
                print(f"  - {p}")
        if report["repaired"]:
            print(f"已修复 {len(report['repaired'])} 项:")
            for r in report["repaired"]:
                print(f"  + {r}")
        if not report["ok"]:
            sys.exit(1)


def cmd_resize(args):
    size = _parse_size(args.size)
    with _open_vfs(args) as vfs:
        before = vfs.df()
        try:
            vfs.grow(size)
        except FSError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
        after = vfs.df()
    print(f"已扩容: {args.image}")
    print(f"  之前: {_human_size(before['total_bytes'])}")
    print(f"  现在: {_human_size(after['total_bytes'])}")


# ---- 多盘卷命令 ----
def cmd_vol_create(args):
    from .volume import create_volume, VALID_MODES
    if args.mode not in VALID_MODES:
        print(f"未知模式: {args.mode}，支持: {VALID_MODES}", file=sys.stderr)
        sys.exit(1)
    paths = args.disks
    disk_size = _parse_size(args.disk_size) if args.disk_size else None
    stripe_size = _parse_size(args.stripe_size) if args.stripe_size else 4096
    vol = create_volume(paths, args.mode, name=args.name,
                        stripe_size=stripe_size, disk_size=disk_size)
    status = vol.status()
    vol.close()
    print(f"已创建卷: {status['name']} ({status['mode_desc']})")
    print(f"  卷 ID:      {status['vol_id']}")
    print(f"  模式:       {status['mode']}")
    print(f"  成员盘数:   {status['ndisks']}")
    print(f"  总块数:     {status['total_blocks']}")
    print(f"  总容量:     {_human_size(status['total_bytes'])}")
    for i, m in enumerate(status['members']):
        print(f"  盘 {i}:       {m['path']} ({m['blocks']} 块)")


def cmd_vol_status(args):
    from .volume import open_volume
    vol = open_volume(args.disks)
    status = vol.status()
    vol.close()
    print(f"卷名:        {status['name']}")
    print(f"卷 ID:       {status['vol_id']}")
    print(f"模式:        {status['mode']} - {status['mode_desc']}")
    print(f"块大小:      {status['block_size']} 字节")
    print(f"总块数:      {status['total_blocks']}")
    print(f"总容量:      {_human_size(status['total_bytes'])}")
    print(f"成员盘数:    {status['ndisks']}")
    for i, m in enumerate(status['members']):
        print(f"  盘 {i}:     {m['path']} ({m['blocks']} 块, uuid={m['uuid'][:8]})")


def cmd_vol_format(args):
    """在已存在的卷上格式化文件系统。"""
    from .volume import open_volume
    from .fs import mkfs
    vol = open_volume(args.disks)
    try:
        mkfs(vol)
    finally:
        vol.close()
    print(f"已在卷上格式化文件系统（{len(args.disks)} 块盘）")


def cmd_vol_add(args):
    """向镜像卷添加一块盘。"""
    from .volume import add_mirror, open_volume
    new_size = _parse_size(args.disk_size) if args.disk_size else None
    add_mirror(args.disks, args.new_disk, new_disk_size=new_size)
    # 重新打开查看状态（add_mirror 返回的卷已关闭）
    all_paths = list(args.disks) + [args.new_disk]
    vol = open_volume(all_paths)
    status = vol.status()
    vol.close()
    print(f"已添加盘 {args.new_disk} 到镜像卷")
    print(f"当前成员盘数: {status['ndisks']}")


def cmd_vol_remove(args):
    """从镜像卷移除一块盘。"""
    from .volume import remove_mirror, open_volume
    remaining = [p for p in args.disks if os.path.abspath(p) != os.path.abspath(args.remove_disk)]
    remove_mirror(args.disks, args.remove_disk)
    vol = open_volume(remaining)
    status = vol.status()
    vol.close()
    print(f"已从镜像卷移除盘 {args.remove_disk}")
    print(f"当前成员盘数: {status['ndisks']}")


def cmd_vol_resync(args):
    """重新同步镜像卷。"""
    from .volume import resync_mirror
    vol = resync_mirror(args.disks)
    vol.close()
    print(f"已重新同步镜像卷（{len(args.disks)} 块盘）")


# ---- 模拟驱动 / 卷标管理 ----
def cmd_scan(args):
    """扫描目录，识别其中的虚拟盘与多盘卷。"""
    from .driver import DiskManager
    mgr = DiskManager(args.dir)
    mgr.scan()
    singles, complete, partial = mgr.assemble()
    print(f"扫描目录: {args.dir}")
    print(f"发现 {len(singles)} 块单盘、{len(complete)} 个完整卷、{len(partial)} 个不完整卷")
    if singles:
        print("\n单盘:")
        for i in singles:
            print(f"  卷标={i.label or '(无)'} uuid={i.disk_uuid[:8]} "
                  f"路径={i.path} ({i.nblocks} 块)")
    if complete:
        print("\n完整卷:")
        for av in complete:
            print(f"  卷名={av.meta.name} vol_id={av.vol_id[:8]} "
                  f"模式={av.meta.mode} 成员={av.needed}")
            for p in av.ordered_paths():
                print(f"    - {p}")
    if partial:
        print("\n不完整卷（成员盘未到齐）:")
        for av in partial:
            print(f"  卷名={av.meta.name} vol_id={av.vol_id[:8]} "
                  f"模式={av.meta.mode} {av.found}/{av.needed}")
    if not singles and not complete and not partial:
        print("（目录下没有可识别的 vdisk 镜像）")


def cmd_mount_all(args):
    """扫描目录并挂载所有可识别的盘/卷，按卷标列出。"""
    from .driver import DiskManager
    mgr = DiskManager(args.dir)
    mgr.scan()
    mgr.mount_all()
    if not mgr.mounted:
        print("没有可挂载的盘/卷")
        return
    print(f"已挂载 {len(mgr.mounted)} 个文件系统（按卷标访问）:")
    for label, m in mgr.mounted.items():
        kind_cn = "单盘" if m.kind == "single" else f"{m.kind}卷"
        print(f"  [{label}] {kind_cn} uuid={m.uuid[:8]}")
        for p in m.paths:
            print(f"    - {p}")
    print("\n提示：卷标即访问入口；在 Python 中可用 DiskManager.get(label).vfs 操作。")


def cmd_label(args):
    """查看或设置一块盘的卷标。"""
    from .identity import probe_disk, write_identity_to_block0
    from .disk import VirtualDisk
    ident = probe_disk(args.image)
    if ident.kind == "unknown":
        print(f"错误: 不是可识别的 vdisk 镜像: {args.image}", file=sys.stderr)
        sys.exit(1)
    if args.label is None:
        # 查询
        print(f"路径:   {args.image}")
        print(f"类型:   {ident.kind}")
        print(f"卷标:   {ident.label or '(无)'}")
        print(f"UUID:   {ident.disk_uuid}")
        if ident.vol_id:
            print(f"卷 ID:  {ident.vol_id}")
        return
    # 设置：只对单盘生效（卷的卷标由卷名管理，用 vol-create --name）
    if ident.is_member:
        print("错误: 多盘卷成员盘的卷标由卷名管理，请用 vol-create --name 设置。",
              file=sys.stderr)
        sys.exit(1)
    d = VirtualDisk(args.image)
    d.open()
    try:
        write_identity_to_block0(d, ident.disk_uuid, "", args.label, is_member=False)
    finally:
        d.close()
    print(f"已设置卷标: {args.label}  (盘 {args.image})")



# ---- 向量数据盘命令 ----
def _json_arg(value):
    try:
        return __import__("json").loads(value)
    except Exception as exc:
        raise ValueError(f"无效 JSON: {value}") from exc

def cmd_vec_create(args):
    from .vector_disk import VectorDisk
    VectorDisk.create(args.image, _parse_size(args.size), label=args.label or "")
    print(f"已创建向量数据盘: {args.image}")

def cmd_vec_collection(args):
    from .vector_disk import VectorDisk
    with VectorDisk(args.image) as disk:
        disk.create_collection(args.name, args.dimension, args.metric, args.max_elements)
    print(f"已创建向量集合: {args.name}")

def cmd_vec_upsert(args):
    from .vector_disk import VectorDisk
    with VectorDisk(args.image) as disk:
        disk.upsert(args.collection, args.id, _json_arg(args.vector), _json_arg(args.metadata))

def cmd_vec_search(args):
    from .vector_disk import VectorDisk
    import json
    where = _json_arg(args.where) if args.where else None
    with VectorDisk(args.image) as disk:
        result = disk.search(args.collection, _json_arg(args.vector), args.k, where)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_vec_get(args):
    from .vector_disk import VectorDisk
    import json
    with VectorDisk(args.image) as disk:
        result = disk.get(args.collection, args.id)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_vec_delete(args):
    from .vector_disk import VectorDisk
    with VectorDisk(args.image) as disk:
        removed = disk.delete(args.collection, args.id)
    print("已删除" if removed else "不存在")

def cmd_vec_list(args):
    from .vector_disk import VectorDisk
    import json
    with VectorDisk(args.image) as disk:
        result = disk.list_collections()
    print(json.dumps(result, ensure_ascii=False, indent=2))



# ---- 日志数据盘命令 ----
def cmd_log_create(args):
    from .log_disk import LogDisk
    LogDisk.create(args.image, _parse_size(args.size), label=args.label or "")
    print(f"已创建日志数据盘: {args.image}")

def cmd_log_stream(args):
    from .log_disk import LogDisk
    with LogDisk(args.image) as disk:
        disk.create_stream(args.name, args.segment_events, args.retention_seconds, args.max_events)
    print(f"已创建日志流: {args.name}")

def cmd_log_emit(args):
    from .log_disk import LogDisk
    with LogDisk(args.image) as disk:
        disk.append(args.stream, level=args.level, logger=args.logger, message=args.message,
                    fields=_json_arg(args.fields), tags=_json_arg(args.tags))

def cmd_log_query(args):
    from .log_disk import LogDisk
    import json
    with LogDisk(args.image) as disk:
        events=disk.query(args.stream,start_ns=args.start_ns,end_ns=args.end_ns,
                          levels=args.level,loggers=args.logger,tags=_json_arg(args.tags),
                          where=_json_arg(args.where) if args.where else None,limit=args.limit,reverse=args.reverse)
    print(json.dumps([e.to_dict() for e in events],ensure_ascii=False,indent=2))

def cmd_log_tail(args):
    from .log_disk import LogDisk
    import json
    with LogDisk(args.image) as disk: events=disk.tail(args.stream,args.count)
    print(json.dumps([e.to_dict() for e in events],ensure_ascii=False,indent=2))

def cmd_log_stats(args):
    from .log_disk import LogDisk
    import json
    with LogDisk(args.image) as disk: result=disk.stats(args.stream)
    print(json.dumps(result,ensure_ascii=False,indent=2))

def cmd_log_compact(args):
    from .log_disk import LogDisk
    with LogDisk(args.image) as disk: count=disk.compact(args.stream)
    print(f"已压缩 {count} 条日志")

def cmd_log_retention(args):
    from .log_disk import LogDisk
    with LogDisk(args.image) as disk: count=disk.enforce_retention(args.stream)
    print(f"已清理 {count} 条日志")

# ---- argparse 构建 ----


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vdisk",
        description="虚拟磁盘管理工具（无需管理员权限）",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def add_image(sp):
        sp.add_argument("image", help="虚拟磁盘镜像文件路径")
        _add_cred_args(sp)

    sp = sub.add_parser("create", help="创建并格式化新磁盘")
    add_image(sp)
    sp.add_argument("--size", required=True, help="磁盘大小，如 16M / 1G / 1048576")
    sp.add_argument("--label", default="", help="卷标（供模拟驱动识别/挂载")
    sp.set_defaults(func=cmd_create)

    sp = sub.add_parser("format", help="重新格式化（覆盖）磁盘")
    add_image(sp)
    sp.add_argument("--size", required=True)
    sp.add_argument("--label", default="", help="卷标")
    sp.set_defaults(func=cmd_format)

    sp = sub.add_parser("info", help="显示磁盘信息")
    add_image(sp)
    sp.set_defaults(func=cmd_info)

    sp = sub.add_parser("status", help="只读显示 DataDisk 与执行运行状态")
    sp.add_argument("image", help="DataDisk 镜像文件路径")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("ls", help="列出目录")
    add_image(sp)
    sp.add_argument("path", nargs="?", default="/")
    sp.add_argument("-l", "--long", action="store_true")
    sp.set_defaults(func=cmd_ls)

    sp = sub.add_parser("mkdir", help="创建目录")
    add_image(sp)
    sp.add_argument("path")
    sp.add_argument("-p", "--parents", action="store_true")
    sp.set_defaults(func=cmd_mkdir)

    sp = sub.add_parser("rmdir", help="删除目录")
    add_image(sp)
    sp.add_argument("path")
    sp.add_argument("-r", "--recursive", action="store_true")
    sp.set_defaults(func=cmd_rmdir)

    sp = sub.add_parser("rm", help="删除文件")
    add_image(sp)
    sp.add_argument("path")
    sp.add_argument("-r", "--recursive", action="store_true")
    sp.set_defaults(func=cmd_rm)

    sp = sub.add_parser("cat", help="输出文件内容")
    add_image(sp)
    sp.add_argument("path")
    sp.set_defaults(func=cmd_cat)

    sp = sub.add_parser("write", help="写入文件（覆盖）")
    add_image(sp)
    sp.add_argument("path")
    sp.add_argument("--file", help="从宿主机文件读取，否则读 stdin")
    sp.set_defaults(func=cmd_write)

    sp = sub.add_parser("append", help="追加到文件")
    add_image(sp)
    sp.add_argument("path")
    sp.add_argument("--file", help="从宿主机文件读取，否则读 stdin")
    sp.set_defaults(func=cmd_append)

    sp = sub.add_parser("touch", help="创建空文件或更新时间戳")
    add_image(sp)
    sp.add_argument("path")
    sp.set_defaults(func=cmd_touch)

    sp = sub.add_parser("cp", help="虚拟磁盘内复制")
    add_image(sp)
    sp.add_argument("src")
    sp.add_argument("dst")
    sp.set_defaults(func=cmd_cp)

    sp = sub.add_parser("mv", help="移动/重命名")
    add_image(sp)
    sp.add_argument("src")
    sp.add_argument("dst")
    sp.set_defaults(func=cmd_mv)

    sp = sub.add_parser("import", help="从宿主机导入文件/目录到虚拟磁盘")
    add_image(sp)
    sp.add_argument("host_path")
    sp.add_argument("vpath")
    sp.add_argument("-r", "--recursive", action="store_true")
    sp.set_defaults(func=cmd_import)

    sp = sub.add_parser("export", help="从虚拟磁盘导出到宿主机")
    add_image(sp)
    sp.add_argument("vpath")
    sp.add_argument("host_path")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("stat", help="查看文件/目录信息")
    add_image(sp)
    sp.add_argument("path")
    sp.set_defaults(func=cmd_stat)

    sp = sub.add_parser("tree", help="树状显示")
    add_image(sp)
    sp.add_argument("path", nargs="?", default="/")
    sp.set_defaults(func=cmd_tree)

    sp = sub.add_parser("mount", help="通过 FUSE 挂载到本地目录（需 fusepy）")
    add_image(sp)
    sp.add_argument("mountpoint")
    sp.set_defaults(func=cmd_mount)

    sp = sub.add_parser("ln", help="创建链接（默认硬链接，-s 为符号链接）")
    add_image(sp)
    sp.add_argument("target")
    sp.add_argument("linkpath")
    sp.add_argument("-s", "--symlink", action="store_true", help="创建符号链接")
    sp.set_defaults(func=cmd_ln)

    sp = sub.add_parser("chmod", help="修改权限模式")
    add_image(sp)
    sp.add_argument("mode", help="八进制权限，如 644、755")
    sp.add_argument("path")
    sp.set_defaults(func=cmd_chmod)

    sp = sub.add_parser("chown", help="修改所有者 uid/gid")
    add_image(sp)
    sp.add_argument("path")
    sp.add_argument("--owner", default=None, help="新属主 uid")
    sp.add_argument("--group", default=None, help="新属组 gid")
    sp.set_defaults(func=cmd_chown)

    sp = sub.add_parser("df", help="显示磁盘使用情况")
    add_image(sp)
    sp.set_defaults(func=cmd_df)

    sp = sub.add_parser("du", help="估算路径占用空间")
    add_image(sp)
    sp.add_argument("path", nargs="?", default="/")
    sp.set_defaults(func=cmd_du)

    sp = sub.add_parser("fsck", help="检查文件系统一致性")
    add_image(sp)
    sp.add_argument("--repair", action="store_true", help="尝试自动修复")
    sp.set_defaults(func=cmd_fsck)

    sp = sub.add_parser("resize", help="扩大磁盘容量（在线，不破坏数据）")
    add_image(sp)
    sp.add_argument("--size", required=True, help="新大小，如 32M / 1G")
    sp.set_defaults(func=cmd_resize)

    # ---- 多盘卷命令 ----
    sp = sub.add_parser("vol-create", help="创建多盘卷（concat/stripe/mirror）")
    sp.add_argument("mode", choices=["concat", "stripe", "mirror"],
                    help="concat=级联 stripe=条带RAID0 mirror=镜像RAID1")
    sp.add_argument("disks", nargs="+", help="成员盘路径（至少 1 块，stripe/mirror 至少 2 块）")
    sp.add_argument("--name", default="", help="卷名")
    sp.add_argument("--disk-size", default=None, help="盘文件不存在时按此大小创建，如 4M")
    sp.add_argument("--stripe-size", default=None, help="条带单元大小（stripe 模式），如 4096")
    sp.set_defaults(func=cmd_vol_create)

    sp = sub.add_parser("vol-status", help="查看卷状态")
    sp.add_argument("disks", nargs="+", help="成员盘路径")
    sp.set_defaults(func=cmd_vol_status)

    sp = sub.add_parser("vol-format", help="在已存在的卷上格式化文件系统")
    sp.add_argument("disks", nargs="+", help="成员盘路径")
    sp.set_defaults(func=cmd_vol_format)

    sp = sub.add_parser("vol-add", help="向镜像卷添加一块盘（从主盘复制数据）")
    sp.add_argument("disks", nargs="+", help="现有成员盘路径")
    sp.add_argument("new_disk", help="新盘路径")
    sp.add_argument("--disk-size", default=None, help="新盘大小（不指定则等于主盘）")
    sp.set_defaults(func=cmd_vol_add)

    sp = sub.add_parser("vol-remove", help="从镜像卷移除一块盘")
    sp.add_argument("disks", nargs="+", help="现有成员盘路径")
    sp.add_argument("remove_disk", help="要移除的盘路径")
    sp.set_defaults(func=cmd_vol_remove)

    sp = sub.add_parser("vol-resync", help="重新同步镜像卷")
    sp.add_argument("disks", nargs="+", help="成员盘路径")
    sp.set_defaults(func=cmd_vol_resync)

    # ---- 模拟驱动 / 卷标管理 ----
    sp = sub.add_parser("scan", help="扫描目录，识别其中的虚拟盘与多盘卷")
    sp.add_argument("dir", help="宿主目录（硬盘柜）路径")
    sp.set_defaults(func=cmd_scan)

    sp = sub.add_parser("mount-all", help="扫描目录并挂载所有盘/卷，按卷标列出")
    sp.add_argument("dir", help="宿主目录路径")
    sp.set_defaults(func=cmd_mount_all)

    sp = sub.add_parser("label", help="查看或设置一块盘的卷标")
    add_image(sp)
    sp.add_argument("label", nargs="?", default=None,
                    help="新卷标；省略则查询当前卷标")
    sp.set_defaults(func=cmd_label)


    sp = sub.add_parser("vec-create", help="创建向量数据盘")
    sp.add_argument("image")
    sp.add_argument("--size", required=True)
    sp.add_argument("--label", default="")
    sp.set_defaults(func=cmd_vec_create)

    sp = sub.add_parser("vec-collection", help="创建向量集合")
    sp.add_argument("image"); sp.add_argument("name"); sp.add_argument("dimension", type=int)
    sp.add_argument("--metric", choices=["cosine", "l2", "ip"], default="cosine")
    sp.add_argument("--max-elements", type=int, default=10000)
    sp.set_defaults(func=cmd_vec_collection)

    sp = sub.add_parser("vec-upsert", help="插入或更新向量")
    sp.add_argument("image"); sp.add_argument("collection"); sp.add_argument("id")
    sp.add_argument("vector", help="JSON 数组"); sp.add_argument("--metadata", default="{}")
    sp.set_defaults(func=cmd_vec_upsert)

    sp = sub.add_parser("vec-search", help="向量相似度搜索")
    sp.add_argument("image"); sp.add_argument("collection"); sp.add_argument("vector")
    sp.add_argument("-k", type=int, default=10); sp.add_argument("--where", default=None)
    sp.set_defaults(func=cmd_vec_search)

    sp = sub.add_parser("vec-get", help="读取向量记录")
    sp.add_argument("image"); sp.add_argument("collection"); sp.add_argument("id")
    sp.set_defaults(func=cmd_vec_get)

    sp = sub.add_parser("vec-delete", help="删除向量记录")
    sp.add_argument("image"); sp.add_argument("collection"); sp.add_argument("id")
    sp.set_defaults(func=cmd_vec_delete)

    sp = sub.add_parser("vec-list", help="列出向量集合")
    sp.add_argument("image"); sp.set_defaults(func=cmd_vec_list)

    sp = sub.add_parser("log-create", help="创建日志数据盘")
    sp.add_argument("image"); sp.add_argument("--size", required=True); sp.add_argument("--label", default="")
    sp.set_defaults(func=cmd_log_create)

    sp = sub.add_parser("log-stream", help="创建日志流")
    sp.add_argument("image"); sp.add_argument("name"); sp.add_argument("--segment-events",type=int,default=1000)
    sp.add_argument("--retention-seconds",type=float); sp.add_argument("--max-events",type=int)
    sp.set_defaults(func=cmd_log_stream)

    sp = sub.add_parser("log-emit", help="写入结构化日志")
    sp.add_argument("image"); sp.add_argument("stream"); sp.add_argument("message")
    sp.add_argument("--level",default="INFO"); sp.add_argument("--logger",default="cli")
    sp.add_argument("--fields",default="{}"); sp.add_argument("--tags",default="{}")
    sp.set_defaults(func=cmd_log_emit)

    sp = sub.add_parser("log-query", help="查询日志")
    sp.add_argument("image"); sp.add_argument("stream"); sp.add_argument("--start-ns",type=int); sp.add_argument("--end-ns",type=int)
    sp.add_argument("--level",action="append"); sp.add_argument("--logger",action="append"); sp.add_argument("--tags",default="{}")
    sp.add_argument("--where"); sp.add_argument("--limit",type=int); sp.add_argument("--reverse",action="store_true")
    sp.set_defaults(func=cmd_log_query)

    sp = sub.add_parser("log-tail", help="读取最新日志")
    sp.add_argument("image"); sp.add_argument("stream"); sp.add_argument("--count",type=int,default=100)
    sp.set_defaults(func=cmd_log_tail)

    for command,func,help_text in [("log-stats",cmd_log_stats,"日志流统计"),("log-compact",cmd_log_compact,"压缩日志流"),("log-retention",cmd_log_retention,"执行保留策略")]:
        sp=sub.add_parser(command,help=help_text); sp.add_argument("image"); sp.add_argument("stream"); sp.set_defaults(func=func)

    from .vscript.cli import add_parser as add_vscript_parser
    add_vscript_parser(sub)

    return p


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
        if isinstance(result, int):
            return result
    except FSError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
