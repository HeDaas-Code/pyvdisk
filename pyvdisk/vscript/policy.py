"""VScript capability and resource policies."""
from __future__ import annotations
import time
from dataclasses import dataclass,field
from typing import Dict,Iterable,Optional,Set
from .errors import CapabilityError,ResourceLimitError

@dataclass
class Policy:
    max_steps:int=1_000_000
    max_wall_time:float=60.0
    max_call_depth:int=128
    max_tasks:int=16
    max_loop_iterations:int=1_000_000
    max_read_bytes:int=256*1024*1024
    max_write_bytes:int=256*1024*1024
    max_output_bytes:int=8*1024*1024
    host_read_roots:list=field(default_factory=list)
    host_write_roots:list=field(default_factory=list)

class Budget:
    def __init__(self,policy:Policy):self.policy=policy;self.started=time.monotonic();self.steps=0;self.read_bytes=0;self.write_bytes=0;self.output_bytes=0
    def tick(self,n=1):
        self.steps+=n
        if self.steps>self.policy.max_steps:raise ResourceLimitError("脚本执行步数超限")
        if time.monotonic()-self.started>self.policy.max_wall_time:raise ResourceLimitError("脚本执行超时")
    def charge_read(self,n):
        self.read_bytes+=n
        if self.read_bytes>self.policy.max_read_bytes:raise ResourceLimitError("脚本读取字节数超限")
    def charge_write(self,n):
        self.write_bytes+=n
        if self.write_bytes>self.policy.max_write_bytes:raise ResourceLimitError("脚本写入字节数超限")
    def charge_output(self,n):
        self.output_bytes+=n
        if self.output_bytes>self.policy.max_output_bytes:raise ResourceLimitError("脚本输出字节数超限")

@dataclass(frozen=True)
class Capability:
    name:str
    kind:str
    permissions:frozenset
    target:object
    root:str="/"
    def require(self,*permissions):
        missing=[p for p in permissions if p not in self.permissions and "admin" not in self.permissions]
        if missing:raise CapabilityError(f"挂载 {self.name} 缺少能力: {', '.join(missing)}")
