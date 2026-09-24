"""VScript compiler and safe runtime public API."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .parser import parse
from .runtime import Runtime, recover_wal
from .policy import Policy, Capability
from .host import HostCapability, HostProxy
from .mounts import MountRegistry
from .stdlib import Handle
from .errors import (VScriptError, LexError, ParseError, CompileError, RuntimeError, CapabilityError, ResourceLimitError)
from .audit import (AuditRecord, script_hash, policy_hash, CheckpointAuditSink, DataDiskAuditSink, AuditSink, PersistentAuditSink)
from .wal import WriteAheadLog, WAL
from .cron import CronExpression, CronError, cron, parse_cron
from .checkpoint import CheckpointStore
from .triggers import Trigger, TriggerRegistry, SchedulerDaemon, Daemon, register_file_trigger, register_log_trigger

@dataclass(frozen=True)
class Program:
    ast: object
    source: str
    filename: str = "<script>"

class Compiler:
    def __init__(self, module_roots=None):
        self.module_roots = tuple(Path(x).resolve() for x in (module_roots or ()))
    def compile(self, source: str, filename: str = "<script>") -> Program:
        tree = parse(source, filename)
        if tree.language != "1.0": raise CompileError(f"不支持的 VScript 语言版本: {tree.language}", tree.span)
        return Program(tree, source, filename)
    def compile_file(self, path) -> Program:
        path = Path(path)
        if path.suffix != ".vds": raise CompileError("VScript 脚本必须使用 .vds 后缀")
        resolved = path.resolve()
        if self.module_roots and not any(resolved == root or root in resolved.parents for root in self.module_roots): raise CompileError("模块路径不在允许的根目录")
        return self.compile(path.read_text(encoding="utf-8"), str(resolved))

def run(source: str, *, filename="<script>", args=None, bindings=None, policy=None, stdout=None, module_roots=None, compiler=None, audit=None, audit_sink=None, audit_callback=None, wal_path=None, wal=None):
    compiler = compiler or Compiler(module_roots=module_roots)
    program = compiler.compile(source, filename)
    sink = audit if audit is not None else audit_sink
    runtime = Runtime(policy=policy, stdout=stdout, compiler=compiler, module_roots=module_roots or getattr(compiler, "module_roots", ()), audit_sink=sink, audit_callback=audit_callback, wal_path=wal_path, wal=wal)
    return runtime.run(program.ast, args=args, bindings=bindings, source=program.source)

def run_file(path, *, args=None, bindings=None, policy=None, stdout=None, module_roots=None, compiler=None, audit=None, audit_sink=None, audit_callback=None):
    compiler = compiler or Compiler(module_roots=module_roots)
    program = compiler.compile_file(path)
    sink = audit if audit is not None else audit_sink
    runtime = Runtime(policy=policy, stdout=stdout, compiler=compiler, module_roots=module_roots or getattr(compiler, "module_roots", ()), audit_sink=sink, audit_callback=audit_callback)
    return runtime.run(program.ast, args=args, bindings=bindings, source=program.source)
