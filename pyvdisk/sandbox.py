"""AgentSandbox: the whole stack behind one object an agent framework can call.

An agent framework needs three things from a sandbox, and this class is exactly
those three:

1. **A confined workspace.**  ``AgentSandbox`` owns a DataDisk image and hands the
   agent a path space inside it.  There is no host path in the API, so a model
   that invents ``../../etc/passwd`` or ``C:\\Windows`` gets a refusal, not a file.
2. **A tool surface.**  :meth:`tools` returns JSON Schemas in the shape OpenAI
   function calling, the Anthropic tool API and MCP all accept, and
   :meth:`dispatch` routes a model's ``(name, arguments)`` back in.  Ten lines of
   framework code is the whole integration.
3. **An audit trail.**  Every call -- including refused ones -- is appended to a
   hash-chained log stream on the same disk, so "what did the agent do" has an
   answer that :meth:`verify_audit` can check for tampering.

The guarantees come from the layers underneath rather than a parallel
implementation: the file verbs go through the capability-scoped view
(:mod:`pyvdisk.infrastructure.capabilities`), the script tool runs on the VScript
runtime with an empty host policy (``host.*`` is unreachable unless you opt in),
and durability is the DataDisk's own transaction log.

    from pyvdisk import AgentSandbox

    with AgentSandbox.create("agent.vdisk") as box:
        box.write("/notes.md", "hello")
        box.dispatch("list_files", {"path": "/"})
"""

from __future__ import annotations

import hashlib
import io
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .contracts import CapabilityGrant, ExecutionContext
from .infrastructure.capabilities import scoped
from .infrastructure.disk import DataDisk
from .vscript import Compiler, MountRegistry, Runtime
from .vscript.audit import AuditRecord, DataDiskAuditSink
from .vscript.policy import Policy

#: Default image size: enough for an agent scratch space, small enough to be fast.
DEFAULT_SIZE = 64 << 20

#: Permission strings the capability layer understands for files.
READ, WRITE, DELETE, ADMIN = "read", "write", "delete", "admin"

#: The audit stream every tool call lands in.
AUDIT_STREAM = "agent-audit"

#: Container bookkeeping the agent must not read or write.  The capability view
#: already guards the three WAL/checkpoint files; these roots go further, because
#: a model that overwrites the manifest or the vector manifest bricks the image it
#: is working in.  They are hidden from listings too, so the agent never sees a
#: path it cannot use.
HIDDEN_ROOTS = ("/.system", "/.vectors", "/.logs")

#: Root-level manifests for those same namespaces (written by ``DataDisk.create``).
HIDDEN_PATHS = ("/.vector_disk.json", "/.log_disk.json")


def _hidden(path: str) -> bool:
    if path in HIDDEN_PATHS:
        return True
    return any(path == root or path.startswith(root + "/") for root in HIDDEN_ROOTS)


class _SandboxFS:
    """The filesystem a VScript program sees: same root, same blind spots.

    The Python verbs go through :meth:`AgentSandbox._visible`; without this the
    script door would be a second entrance to the same image with different
    rules, and ``fs.listdir(sandbox, "/")`` would hand the model the very paths
    ``list_files`` refuses to show it.  Paths are translated here and the calls
    are forwarded, so the capability-scoped namespace underneath still applies.
    """

    def __init__(self, target: Any, translate: Any):
        self._target = target
        self._translate = translate

    def __getattr__(self, name: str):
        """Everything without a path (``df``, ``fsck``, ...) is passed straight on."""
        return getattr(object.__getattribute__(self, "_target"), name)

    @staticmethod
    def _keep(top: str, name: str) -> bool:
        return not _hidden(f"{top.rstrip('/')}/{name}")

    def listdir(self, path: str = "/") -> List[str]:
        directory = self._translate(path)
        return [name for name in self._target.listdir(directory) if self._keep(directory, name)]

    def listdir_with_stat(self, path: str = "/") -> List[Any]:
        """Names plus stats, hidden entries dropped.

        Built from ``listdir`` + ``stat`` rather than forwarded: the scoped
        namespace the sandbox uses does not expose the bulk variant.
        """
        directory = self._translate(path).rstrip("/") or "/"
        return [(name, self._target.stat(f"{directory}/{name}" if directory != "/" else f"/{name}"))
                for name in self._target.listdir(directory) if self._keep(directory, name)]

    def walk(self, path: str = "/"):
        """Walk the visible tree.

        The underlying walk yields a directory even when every child is filtered,
        so hidden roots have to be dropped as tops too -- otherwise ``fs.walk``
        (and ``fs.glob``, which is built on it) would still name ``/.system``.
        """
        for top, dirs, files in self._target.walk(self._translate(path)):
            if _hidden(top):
                continue
            yield (top,
                   [name for name in dirs if self._keep(top, name)],
                   [name for name in files if self._keep(top, name)])

    def _forward(self, method: str, path: str, *args: Any, **kwargs: Any) -> Any:
        return getattr(self._target, method)(self._translate(path), *args, **kwargs)

    def exists(self, path: str = "/") -> bool:
        target = self._translate(path)
        return False if _hidden(target) else self._target.exists(target)

    def isfile(self, path: str) -> bool:
        target = self._translate(path)
        return False if _hidden(target) else self._target.isfile(target)

    def isdir(self, path: str) -> bool:
        target = self._translate(path)
        return False if _hidden(target) else self._target.isdir(target)

    def stat(self, path: str) -> Any:
        return self._forward("stat", path)

    def read_file(self, path: str) -> bytes:
        return self._forward("read_file", path)

    def write_file(self, path: str, data: Any) -> Any:
        return self._forward("write_file", path, data)

    def append_file(self, path: str, data: Any) -> Any:
        return self._forward("append_file", path, data)

    def mkdir(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("mkdir", path, *args, **kwargs)

    def makedirs(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("makedirs", path, *args, **kwargs)

    def remove(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("remove", path, *args, **kwargs)

    def rmtree(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("rmtree", path, *args, **kwargs)

    def rename(self, source: str, destination: str, *args: Any, **kwargs: Any) -> Any:
        return self._target.rename(self._translate(source), self._translate(destination), *args, **kwargs)

    def move(self, source: str, destination: str, *args: Any, **kwargs: Any) -> Any:
        return self._target.move(self._translate(source), self._translate(destination), *args, **kwargs)

    def copy(self, source: str, destination: str, *args: Any, **kwargs: Any) -> Any:
        return self._target.copy(self._translate(source), self._translate(destination), *args, **kwargs)

    def link(self, source: str, destination: str, *args: Any, **kwargs: Any) -> Any:
        return self._target.link(self._translate(source), self._translate(destination), *args, **kwargs)

    def symlink(self, source: str, destination: str, *args: Any, **kwargs: Any) -> Any:
        return self._target.symlink(self._translate(source), self._translate(destination), *args, **kwargs)

    def open(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("open", path, *args, **kwargs)

    def du(self, path: str = "/") -> Any:
        return self._forward("du", path)

    def readlink(self, path: str) -> Any:
        return self._forward("readlink", path)

    def truncate(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("truncate", path, *args, **kwargs)

    def chmod(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("chmod", path, *args, **kwargs)

    def chown(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("chown", path, *args, **kwargs)

    def utime(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._forward("utime", path, *args, **kwargs)


class SandboxError(Exception):
    """The sandbox refused an operation before it reached the disk."""


@dataclass(frozen=True)
class ToolResult:
    """Outcome of one tool call, in a shape that is easy to log or assert on."""

    ok: bool
    content: str
    tool: str = ""
    error: Optional[str] = None

    def __str__(self) -> str:
        return self.content


#: The tool surface.  ``mutates`` decides whether a read-only sandbox offers it.
TOOLS: Tuple[Dict[str, Any], ...] = (
    {
        "name": "write_file",
        "description": "Create or overwrite a text file inside the sandbox. Parent directories are created.",
        "mutates": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute sandbox path, e.g. /report.md"},
                "content": {"type": "string", "description": "File content (UTF-8)"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file from the sandbox.",
        "mutates": False,
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Absolute sandbox path"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_files",
        "description": "List the entries of a sandbox directory with their size and type.",
        "mutates": False,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory to list (default /)"},
                "recursive": {"type": "boolean", "description": "Walk subdirectories too"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "make_directory",
        "description": "Create a directory (and any missing parents) inside the sandbox.",
        "mutates": True,
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory path"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file, or a directory when recursive is true.",
        "mutates": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to delete"},
                "recursive": {"type": "boolean", "description": "Allow deleting a non-empty directory"},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_script",
        "description": (
            "Run a VScript program against this sandbox. The disk is bound as the variable "
            "'sandbox': fs.write(sandbox, \"/a.txt\", \"hi\"), fs.read_text(sandbox, \"/a.txt\"), "
            "fs.listdir(sandbox, \"/\"). Host access is not available. "
            "Returns whatever the script printed."
        ),
        "mutates": True,
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "VScript source code"},
                "args": {
                    "type": "object",
                    "description": "String arguments exposed to the script via arg(name)",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["source"],
            "additionalProperties": False,
        },
    },
)

_BY_NAME = {tool["name"]: tool for tool in TOOLS}


def _canonical(arguments: Mapping[str, Any]) -> str:
    return json.dumps(arguments, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _hash_call(tool: str, arguments: Mapping[str, Any]) -> str:
    return hashlib.sha256(f"{tool}\x00{_canonical(arguments)}".encode("utf-8")).hexdigest()


class AgentSandbox:
    """A confined, audited workspace with an agent-shaped tool interface."""

    def __init__(self, disk: DataDisk, *, name: str = "sandbox", read_only: bool = False,
                 allow_delete: bool = True, run_id: Optional[str] = None,
                 script_timeout: float = 10.0, script_output_bytes: int = 256 * 1024,
                 script_write_bytes: int = 8 << 20,
                 host_read_roots: Sequence[str] = (), host_write_roots: Sequence[str] = (),
                 audit_stream: str = AUDIT_STREAM, audit_max_events: Optional[int] = 10000,
                 audit: bool = True):
        if not getattr(disk, "mounted", False):
            disk = disk.mount()
        self.disk = disk
        self.name = name
        self.read_only = bool(read_only)
        self.allow_delete = bool(allow_delete) and not self.read_only
        self.run_id = run_id or hashlib.sha256(f"{time.time_ns()}:{id(self)}".encode()).hexdigest()[:16]
        self.script_timeout = float(script_timeout)
        self.script_output_bytes = int(script_output_bytes)
        self.script_write_bytes = int(script_write_bytes)
        self.host_read_roots = tuple(host_read_roots)
        self.host_write_roots = tuple(host_write_roots)
        self.audit_stream = audit_stream
        self.audit_max_events = audit_max_events
        self._calls = 0
        self._failures = 0

        permissions = {READ}
        if not self.read_only:
            permissions.add(WRITE)
            if self.allow_delete:
                permissions.add(DELETE)
        self._permissions = frozenset(permissions)
        # The verbs go through the capability-scoped view, so a read-only sandbox
        # refuses a write at the governance layer even if a caller reaches past
        # the tool surface and calls write() directly.
        self._context = ExecutionContext(
            run_id=self.run_id,
            # "*" is how the governance layer spells "every namespace": the grant
            # is matched by name against fs/vector/log/checkpoint, so naming it
            # after the sandbox would match none of them and refuse everything.
            capabilities=(CapabilityGrant(name="*", permissions=self._permissions, scope="/"),),
        )
        self._scoped = scoped(disk, self._context)
        self._sink = None
        if audit:
            self._sink = self._open_sink()

    # ---- construction ----------------------------------------------------

    @classmethod
    def create(cls, path: str, *, size_bytes: int = DEFAULT_SIZE, label: str = "agent sandbox",
               **options: Any) -> "AgentSandbox":
        """Create a new sandbox image and return it, mounted."""
        DataDisk.create(path, size_bytes, label=label)
        return cls(DataDisk(path).mount(), **options)

    @classmethod
    def open(cls, path: str, **options: Any) -> "AgentSandbox":
        """Open an existing sandbox image."""
        return cls(DataDisk(path).mount(), **options)

    def _open_sink(self) -> DataDiskAuditSink:
        streams = self.disk.logs.list_streams()
        names = {item if isinstance(item, str) else item.get("name") for item in streams}
        if self.audit_stream not in names:
            self.disk.logs.create_stream(self.audit_stream, max_events=self.audit_max_events)
        return DataDiskAuditSink(self.disk, stream=self.audit_stream, chained=True)

    # ---- filesystem verbs ------------------------------------------------

    def _normalize(self, path: Any) -> str:
        """Map anything a model sends onto a path inside the sandbox.

        ``C:\\Windows`` becomes ``/C:/Windows`` -- a directory inside the image,
        never the host path it looks like.  ``..`` is refused outright rather
        than resolved, so the refusal is visible in the audit trail.
        """
        if not isinstance(path, str) or not path.strip():
            raise SandboxError("path must be a non-empty string")
        if "\x00" in path:
            raise SandboxError("path contains NUL")
        parts: List[str] = []
        for part in path.replace("\\", "/").split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                raise SandboxError("path may not escape the sandbox root")
            parts.append(part)
        return "/" + "/".join(parts)

    def _visible(self, path: Any) -> str:
        """Normalize, then refuse the container's own bookkeeping paths."""
        target = self._normalize(path)
        if _hidden(target):
            raise SandboxError(f"{target} is container bookkeeping and is not accessible")
        return target

    def _parents(self, path: str) -> List[str]:
        segments = [p for p in path.strip("/").split("/")[:-1] if p]
        out, seen = [], ""
        for name in segments:
            seen = f"{seen}/{name}"
            out.append(seen)
        return out

    def write(self, path: str, content: Any) -> int:
        """Write ``content`` to ``path``, creating parent directories."""
        target = self._visible(path)
        raw = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        for parent in self._parents(target):
            if not self._scoped.fs.exists(parent):
                self._scoped.fs.makedirs(parent)
        self._scoped.fs.write_file(target, raw)
        return len(raw)

    def read(self, path: str) -> bytes:
        """Read the raw bytes at ``path``."""
        return self._scoped.fs.read_file(self._visible(path))

    def read_text(self, path: str, encoding: str = "utf-8", errors: str = "replace") -> str:
        return self.read(path).decode(encoding, errors)

    def list(self, path: str = "/", recursive: bool = False) -> List[Dict[str, Any]]:
        """Entries under ``path``, each with its name, type and size."""
        target = self._visible(path)
        entries: List[Dict[str, Any]] = []

        def collect(directory: str) -> None:
            for name in self._scoped.fs.listdir(directory):
                child = f"{directory.rstrip('/')}/{name}"
                if _hidden(child):
                    continue
                stat = self._scoped.fs.stat(child)
                entries.append({"path": child, "type": "dir" if stat.is_dir else "file", "size": stat.size})
                if recursive and stat.is_dir:
                    collect(child)

        collect(target)
        return entries

    def delete(self, path: str, recursive: bool = False) -> None:
        """Delete a file, or a directory when ``recursive``."""
        target = self._visible(path)
        if self._scoped.fs.isdir(target):
            if not recursive:
                raise SandboxError("path is a directory; pass recursive=true to delete it")
            self._scoped.fs.rmtree(target)
        else:
            self._scoped.fs.remove(target)

    def make_directory(self, path: str) -> str:
        target = self._visible(path)
        self._scoped.fs.makedirs(target)
        return target

    def exists(self, path: str) -> bool:
        target = self._normalize(path)
        return False if _hidden(target) else self._scoped.fs.exists(target)

    def run(self, source: str, *, args: Optional[Mapping[str, str]] = None,
            timeout: Optional[float] = None) -> str:
        """Run a VScript program with this sandbox bound as ``sandbox``.

        The host policy is empty unless the sandbox was constructed with host
        roots, so ``host.read``/``host.write`` fail even though the language
        supports them.
        """
        permissions = set(self._permissions)
        registry = MountRegistry()
        handle = registry.grant(self.name, "fs", _SandboxFS(self._scoped.fs, self._visible),
                                permissions=permissions, root="/")
        policy = Policy(
            max_wall_time=self.script_timeout if timeout is None else float(timeout),
            max_write_bytes=self.script_write_bytes,
            max_output_bytes=self.script_output_bytes,
            host_read_roots=list(self.host_read_roots),
            host_write_roots=list(self.host_write_roots),
        )
        buffer = io.StringIO()
        runtime = Runtime(policy=policy, stdout=buffer, mount_registry=registry,
                          allowed_mounts={self.name: permissions})
        try:
            program = Compiler().compile(source, "<agent-sandbox>")
            value = runtime.run(program.ast, args=dict(args or {}), bindings={self.name: handle}, source=source)
        finally:
            registry.close()
        text = buffer.getvalue()
        if value is not None:
            rendered = runtime.stringify(value)
            if rendered and rendered != "null":
                text = f"{text}{rendered}\n"
        return text

    # ---- tool surface ----------------------------------------------------

    def tools(self, style: str = "openai") -> List[Dict[str, Any]]:
        """Tool definitions for the framework's own calling convention.

        ``openai`` and ``anthropic`` share ``{name, description, parameters}``;
        ``mcp`` renames the schema key to ``inputSchema``.
        """
        if style not in ("openai", "anthropic", "mcp"):
            raise SandboxError(f"unknown tool style: {style}")
        key = "inputSchema" if style == "mcp" else "parameters"
        out = []
        for tool in TOOLS:
            if self.read_only and tool["mutates"]:
                continue
            if tool["name"] == "delete_file" and not self.allow_delete:
                continue
            out.append({"name": tool["name"], "description": tool["description"], key: tool["parameters"]})
        return out

    def call(self, name: str, arguments: Optional[Mapping[str, Any]] = None) -> ToolResult:
        """Run one tool call and audit it, whatever the outcome."""
        arguments = dict(arguments or {})
        started = time.time()
        try:
            content = self._invoke(name, arguments)
            result = ToolResult(True, content, name)
        except Exception as exc:  # noqa: BLE001 - every failure is reported to the model
            message = f"{type(exc).__name__}: {exc}"
            result = ToolResult(False, message, name, error=message)
        self._record(name, arguments, result, started)
        return result

    def dispatch(self, name: str, arguments: Optional[Mapping[str, Any]] = None) -> str:
        """What a framework feeds back to the model: always a string."""
        return str(self.call(name, arguments))

    def _invoke(self, name: str, arguments: Mapping[str, Any]) -> str:
        if name not in _BY_NAME:
            raise SandboxError(f"unknown tool: {name}")
        spec = _BY_NAME[name]
        if self.read_only and spec["mutates"]:
            raise SandboxError(f"{name} is not available: sandbox is read-only")
        if name == "delete_file" and not self.allow_delete:
            raise SandboxError("delete_file is not available: deletion is disabled")
        missing = [key for key in spec["parameters"].get("required", []) if key not in arguments]
        if missing:
            raise SandboxError(f"missing required argument(s): {', '.join(missing)}")
        if name == "write_file":
            written = self.write(arguments["path"], arguments["content"])
            return f"wrote {written} bytes to {self._normalize(arguments['path'])}"
        if name == "read_file":
            data = self.read(arguments["path"])
            text = data.decode("utf-8", "replace")
            return text if len(text) <= 200000 else f"{text[:200000]}\n... [{len(data)} bytes total]"
        if name == "list_files":
            entries = self.list(arguments.get("path", "/"), bool(arguments.get("recursive", False)))
            if not entries:
                return f"{self._normalize(arguments.get('path', '/'))}: empty"
            lines = [f"{'dir ' if e['type'] == 'dir' else 'file'} {e['size']:>9} {e['path']}" for e in entries]
            return "\n".join(lines)
        if name == "make_directory":
            return f"created {self.make_directory(arguments['path'])}"
        if name == "delete_file":
            target = self._normalize(arguments["path"])
            self.delete(arguments["path"], bool(arguments.get("recursive", False)))
            return f"deleted {target}"
        if name == "run_script":
            output = self.run(arguments["source"], args=arguments.get("args"))
            return output if output else "(script produced no output)"
        raise SandboxError(f"tool {name} has no implementation")

    # ---- audit -----------------------------------------------------------

    def _record(self, tool: str, arguments: Mapping[str, Any], result: ToolResult, started: float) -> None:
        self._calls += 1
        if not result.ok:
            self._failures += 1
        if self._sink is None:
            return
        metrics = {
            "tool": tool,
            "arguments": json.loads(_canonical(arguments)),
            "duration_ms": round((time.time() - started) * 1000.0, 3),
            "ok": result.ok,
            "result_bytes": len(result.content.encode("utf-8")),
        }
        error = {"type": "SandboxError", "message": result.error} if result.error else None
        self._sink.emit(AuditRecord(
            run_id=self.run_id,
            script_hash=_hash_call(tool, arguments),
            policy_hash=self._policy_hash(),
            status="success" if result.ok else "failure",
            metrics=metrics,
            error=error,
            started_at=started,
            finished_at=time.time(),
            capability_summary={"name": self.name, "permissions": sorted(self._permissions)},
        ))

    def _policy_hash(self) -> str:
        payload = _canonical({
            "read_only": self.read_only,
            "allow_delete": self.allow_delete,
            "host_read_roots": list(self.host_read_roots),
            "host_write_roots": list(self.host_write_roots),
            "script_timeout": self.script_timeout,
        })
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def audit(self, **filters: Any) -> List[Dict[str, Any]]:
        """Audit rows, oldest first.

        Filters are the sink's own (``run_id``, ``status``, ``since``, ``until``,
        ``limit``, ``newest_first``) plus ``tool``, which selects on the tool name
        recorded in the row's metrics.
        """
        if self._sink is None:
            return []
        tool = filters.pop("tool", None)
        rows = list(self._sink.query(**filters))
        if tool is not None:
            rows = [row for row in rows if (row.get("metrics") or {}).get("tool") == tool]
        return rows

    def verify_audit(self) -> Dict[str, Any]:
        """Check the hash chain over the audit stream."""
        if self._sink is None:
            return {"ok": True, "length": 0, "reason": "audit disabled"}
        return self._sink.verify()

    def retain_audit(self) -> Dict[str, Any]:
        """Ask the log layer to enforce the stream's retention policy now."""
        if self._sink is None:
            return {"kept": 0, "dropped": 0}
        return self._sink.retain()

    # ---- lifecycle -------------------------------------------------------

    @property
    def calls(self) -> int:
        return self._calls

    @property
    def failures(self) -> int:
        return self._failures

    def stats(self) -> Dict[str, Any]:
        usage = self._scoped.fs.df()
        return {
            "name": self.name,
            "run_id": self.run_id,
            "read_only": self.read_only,
            "tools": [tool["name"] for tool in self.tools()],
            "calls": self._calls,
            "failures": self._failures,
            "disk": usage,
        }

    def close(self) -> None:
        self.disk.close()

    def __enter__(self) -> "AgentSandbox":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = ["AgentSandbox", "SandboxError", "ToolResult", "TOOLS", "DEFAULT_SIZE", "AUDIT_STREAM"]
