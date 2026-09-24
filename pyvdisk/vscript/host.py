"""Capability-confined host filesystem bridge for VScript."""
from __future__ import annotations
import os
import stat
import tempfile
from .errors import CapabilityError, RuntimeError

class HostCapability:
    def __init__(self, read_roots=(), write_roots=()):
        self.read_roots = tuple(_root(x) for x in (read_roots or ()))
        self.write_roots = tuple(_root(x) for x in (write_roots or ()))
    def proxy(self):
        return HostProxy(self)

def _root(path):
    p = os.path.realpath(os.fspath(path))
    if not os.path.isdir(p):
        raise CapabilityError("宿主授权根目录不存在或不是目录")
    return p

class HostProxy:
    def __init__(self, capability): self.capability = capability
    def _check(self, path, write=False, create=False):
        raw = os.path.abspath(os.fspath(path))
        if not raw or "\x00" in raw: raise CapabilityError("宿主路径无效")
        roots = self.capability.write_roots if write else self.capability.read_roots
        if not roots:
            # An empty root list is a policy that granted nothing, not a bad path:
            # say which switch grants it instead of blaming the caller's argument.
            raise CapabilityError(
                "宿主%s未授权：启动时用 --host-%s-root 指定允许的根目录"
                % ("写入" if write else "读取", "write" if write else "read"))
        resolved = os.path.realpath(raw)
        if not any(os.path.commonpath((resolved, r)) == r for r in roots):
            raise CapabilityError("宿主路径不在允许的根目录")
        # Reject symlinks in the requested path, including a final symlink.
        probe = raw if os.path.lexists(raw) else (os.path.dirname(raw) if create else raw)
        current = os.path.sep
        for part in probe.strip(os.path.sep).split(os.path.sep):
            current = os.path.join(current, part)
            if os.path.islink(current): raise CapabilityError("不允许通过符号链接访问宿主路径")
        if os.path.lexists(raw):
            mode = os.lstat(raw).st_mode
            if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise CapabilityError("不允许访问特殊文件")
        return resolved
    def read(self, path):
        p = self._check(path)
        try:
            if not stat.S_ISREG(os.stat(p, follow_symlinks=False).st_mode):
                raise CapabilityError("宿主路径不是普通文件")
            with open(p, "rb") as f: return f.read()
        except OSError as e: raise RuntimeError("读取宿主文件失败") from e
    def write(self, path, data, overwrite=True):
        p = self._check(path, write=True, create=True)
        if os.path.lexists(p) and not overwrite: raise RuntimeError("目标已存在")
        if os.path.lexists(p) and not stat.S_ISREG(os.lstat(p).st_mode): raise CapabilityError("目标不是普通文件")
        if not os.path.isdir(os.path.dirname(p)): raise RuntimeError("目标父目录不存在")
        raw_data = data.encode() if isinstance(data, str) else bytes(data)
        parent = os.path.dirname(p)
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(p) + ".", dir=parent)
            with os.fdopen(fd, "wb") as f:
                f.write(raw_data)
                f.flush()
                os.fsync(f.fileno())
            if os.path.lexists(p) and not overwrite:
                raise RuntimeError("目标已存在")
            if os.path.lexists(p) and not stat.S_ISREG(os.lstat(p).st_mode):
                raise CapabilityError("目标不是普通文件")
            os.replace(tmp, p)
            tmp = None
            dirfd = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        except OSError as e: raise RuntimeError("写入宿主文件失败") from e
        finally:
            if tmp is not None:
                try: os.unlink(tmp)
                except OSError: pass
        return len(raw_data)

def create_host_module(runtime):
    from .stdlib import NativeModule, NativeFunction
    proxy = HostCapability(runtime.policy.host_read_roots, runtime.policy.host_write_roots).proxy()
    def read(path):
        data = proxy.read(path); runtime.budget.charge_read(len(data)); return data
    def write(path, data, overwrite=True):
        raw = data.encode() if isinstance(data, str) else bytes(data); runtime.budget.charge_write(len(raw)); return proxy.write(path, raw, overwrite)
    def import_file(path, handle, destination):
        handle.cap.require("write"); data = proxy.read(path); runtime.budget.charge_read(len(data)); runtime.budget.charge_write(len(data)); handle.cap.target.write_file(destination, data); return len(data)
    def export_file(handle, source, path, overwrite=True):
        handle.cap.require("read"); data = handle.cap.target.read_file(source); runtime.budget.charge_read(len(data)); runtime.budget.charge_write(len(data)); return proxy.write(path, data, overwrite)
    funcs = {"read": read, "write": write, "import_file": import_file, "export_file": export_file}
    return NativeModule("host", {k: NativeFunction("host." + k, v) for k, v in funcs.items()})
