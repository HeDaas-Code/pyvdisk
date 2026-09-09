"""VScript mount registry and capability grants."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict,Iterable,Optional
from ..identity import probe_disk
from ..vfs import VFS
from ..vector_disk import VectorDisk
from ..log_disk import LogDisk
from .errors import CapabilityError
from .policy import Capability
from .stdlib import Handle

DEFAULT_PERMISSIONS={
 "fs":{"read"},
 "vector":{"read","query"},
 "log":{"query"},
}

class MountRegistry:
    def __init__(self):self._caps:Dict[str,Capability]={};self._owned=[]
    def grant(self,name,kind,target,permissions=None,root="/"):
        if name in self._caps:raise CapabilityError(f"重复挂载名: {name}")
        if kind not in DEFAULT_PERMISSIONS:raise CapabilityError(f"未知挂载类型: {kind}")
        cap=Capability(name,kind,frozenset(permissions or DEFAULT_PERMISSIONS[kind]),target,root)
        self._caps[name]=cap;return Handle(cap)
    def open(self,name,path,kind=None,permissions=None,root="/"):
        ident=probe_disk(path);actual={"single":"fs","member":"fs","vector":"vector","log":"log"}.get(ident.kind)
        if actual is None:raise CapabilityError(f"无法识别磁盘: {path}")
        if kind and kind!=actual:raise CapabilityError(f"磁盘类型不匹配: 期望 {kind}，实际 {actual}")
        if actual=="fs":target=VFS(path).mount()
        elif actual=="vector":target=VectorDisk(path).mount()
        else:target=LogDisk(path).mount()
        self._owned.append(target);return self.grant(name,actual,target,permissions,root)
    def get(self,name):
        if name not in self._caps:raise CapabilityError(f"未授权挂载: {name}")
        return Handle(self._caps[name])
    def handles(self):return {name:Handle(cap) for name,cap in self._caps.items()}
    def close(self):
        for obj in reversed(self._owned):
            try:obj.close()
            except Exception:pass
        self._owned.clear();self._caps.clear()
    def __enter__(self):return self
    def __exit__(self,*exc):self.close()
