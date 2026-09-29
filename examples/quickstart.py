#!/usr/bin/env python3
"""PyVDisk quickstart: one file, standard library only, Windows or Linux.

    python examples/quickstart.py [workdir]

Nothing here needs hnswlib, fusepy, NumPy or root privileges.  The vector disk
falls back to a built-in flat index, FUSE is not used at all, and every artifact
is a plain file in the work directory (a temporary one by default).

It walks the stack bottom-up: a block device, a filesystem, a transaction, a
vector collection, a log stream, a VScript program, and finally the AgentSandbox
that wraps all of it for an agent framework.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile

# Run straight from a checkout: `python examples/quickstart.py` puts examples/ on
# sys.path, not the repository root.  If pyvdisk is not installed, add the root.
if importlib.util.find_spec("pyvdisk") is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyvdisk import (  # noqa: E402 - path fix above has to run first
    AgentSandbox,
    DataDisk,
    LogDisk,
    VFS,
    VectorDisk,
    __version__,
    compat,
)


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def block_device(work: str) -> str:
    """Layer 1: a plain file used as a block device."""
    path = os.path.join(work, "blocks.vdisk")
    VFS.create(path, 16 * 1024 * 1024, label="quickstart")
    with VFS(path) as vfs:
        vfs.makedirs("/docs")
        vfs.write_file("/docs/hello.txt", b"hello from a virtual block device")
        print("read back:", vfs.read_file("/docs/hello.txt").decode())
        usage = vfs.df()
        print("usage:", {key: usage[key] for key in list(usage)[:3]})
    return path


def transactions(work: str) -> str:
    """Layer 2: a data container with a write-ahead log."""
    path = os.path.join(work, "data.vdisk")
    DataDisk.create(path, 32 * 1024 * 1024, label="quickstart data")
    with DataDisk(path) as disk:
        disk.fs.write_file("/kept.txt", b"committed")
        try:
            with disk.transaction():
                # Writes inside the block are journalled by the transaction and
                # undone when it is left through an exception.
                disk.fs.write_file("/rolled-back.txt", b"never visible")
                raise RuntimeError("changed my mind")
        except RuntimeError as exc:
            print("transaction aborted:", exc)
        print("kept.txt exists:", disk.fs.exists("/kept.txt"))
        print("rolled-back.txt exists:", disk.fs.exists("/rolled-back.txt"))
        disk.checkpoints.set("last-run", {"ok": True})
        disk.checkpoints.save()
        print("checkpoint:", disk.checkpoints.get("last-run"))
    return path


def vectors(work: str) -> str:
    """Layer 3: a vector collection -- with or without hnswlib."""
    from pyvdisk.vector_disk import _index_backend

    path = os.path.join(work, "vectors.vdisk")
    VectorDisk.create(path, 32 * 1024 * 1024, label="embeddings")
    backend = getattr(_index_backend(), "__name__", "flat")
    with VectorDisk(path) as disk:
        disk.create_collection("docs", 3, metric="cosine")
        disk.upsert_many("docs", [
            {"id": "intro", "vector": [1.0, 0.0, 0.0], "metadata": {"kind": "guide"}},
            {"id": "api", "vector": [0.9, 0.1, 0.0], "metadata": {"kind": "reference"}},
            {"id": "faq", "vector": [0.0, 1.0, 0.0], "metadata": {"kind": "guide"}},
        ])
        hits = disk.search("docs", [1.0, 0.0, 0.0], k=2)
        print("index backend:", "hnswlib" if backend == "hnswlib" else "built-in flat (no dependency)")
        print("nearest:", [(hit["id"], round(hit["distance"], 4)) for hit in hits])
        print("filtered:", [hit["id"] for hit in disk.search("docs", [1.0, 0.0, 0.0], k=3, where={"kind": "guide"})])
    return path


def logs(work: str) -> str:
    """Layer 4: an append-only log with retention."""
    path = os.path.join(work, "logs.vdisk")
    LogDisk.create(path, 16 * 1024 * 1024, label="events")
    with LogDisk(path) as disk:
        disk.create_stream("app", segment_events=2, max_events=100)
        for index in range(5):
            disk.append("app", level="INFO", logger="quickstart", message=f"event {index}", fields={"i": index})
        print("events:", disk.count("app"))
        print("tail:", [event.message for event in disk.tail("app", 2)])
        print("query INFO:", len(disk.query("app", levels=["INFO"])))
    return path


def script(work: str) -> None:
    """Layer 5: a sandboxed VScript program."""
    from pyvdisk.vscript import Compiler, MountRegistry, Runtime
    from pyvdisk.vscript.policy import Policy

    path = os.path.join(work, "script.vdisk")
    VFS.create(path, 8 * 1024 * 1024)
    with VFS(path) as vfs, MountRegistry() as registry:
        handle = registry.grant("store", "fs", vfs, permissions={"read", "write"}, root="/")
        source = (
            'import std.fs as fs;\n'
            'fs.write(store, "/hello.txt", "written by VScript");\n'
            'print("script read:", fs.read_text(store, "/hello.txt"));\n'
        )
        runtime = Runtime(policy=Policy(max_wall_time=5.0), stdout=sys.stdout,
                          mount_registry=registry, allowed_mounts={"store": {"read", "write"}})
        runtime.run(Compiler().compile(source, "<quickstart>").ast, bindings={"store": handle}, source=source)


def agent_sandbox(work: str) -> None:
    """Layer 6: the object an agent framework talks to."""
    path = os.path.join(work, "agent.vdisk")
    with AgentSandbox.create(path, size_bytes=32 * 1024 * 1024) as box:
        print("tools:", ", ".join(tool["name"] for tool in box.tools()))
        print(box.dispatch("write_file", {"path": "/notes.md", "content": "# findings\n- it works\n"}))
        print(box.dispatch("list_files", {"path": "/", "recursive": True}))
        print("refused:", box.dispatch("read_file", {"path": "../../etc/passwd"}))
        report = box.verify_audit()
        print(f"audit: {report['length']} chained records, chain ok = {report['ok']}")


def main(argv: list[str]) -> int:
    work = argv[1] if len(argv) > 1 else tempfile.mkdtemp(prefix="pyvdisk-quickstart-")
    os.makedirs(work, exist_ok=True)
    print(f"pyvdisk {__version__} on {sys.platform} (compat: {compat.describe()['implementation']})")
    print("work directory:", work)
    section("1. block device + filesystem")
    block_device(work)
    section("2. transactions and checkpoints")
    transactions(work)
    section("3. vector search")
    vectors(work)
    section("4. structured logs")
    logs(work)
    section("5. VScript")
    script(work)
    section("6. AgentSandbox")
    agent_sandbox(work)
    print("\nDone. Everything above was plain files in", work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
