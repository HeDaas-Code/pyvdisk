"""AgentSandbox: the confinement, the tool surface and the audit trail.

These are the properties an agent framework is trusting when it hands this object
to a model, so they are tested as promises rather than as implementation:

* the path space is the image, not the host -- ``..``, ``C:\\Windows`` and the
  container's own bookkeeping are refused;
* a read-only sandbox refuses writes at the governance layer, not just by hiding
  the tool;
* every call, including every refusal, lands in a hash-chained audit stream;
* ``run_script`` cannot reach the host, and its output is bounded so a script
  cannot flood the model's context.
"""
from __future__ import annotations

import json

import pytest

from pyvdisk import DataDisk
from pyvdisk.sandbox import AUDIT_STREAM, TOOLS, AgentSandbox, SandboxError
from pyvdisk.vscript.audit import DataDiskAuditSink
from pyvdisk.vscript.errors import CapabilityError


@pytest.fixture
def box(tmp_path):
    with AgentSandbox.create(str(tmp_path / "agent.vdisk"), size_bytes=32 << 20) as sandbox:
        yield sandbox


def test_create_then_reopen_keeps_the_workspace(tmp_path):
    path = str(tmp_path / "agent.vdisk")
    with AgentSandbox.create(path) as first:
        first.dispatch("write_file", {"path": "/notes.md", "content": "kept"})
        run_id = first.run_id
    with AgentSandbox.open(path) as second:
        assert second.read_text("/notes.md") == "kept"
        assert second.run_id != run_id
        assert second.verify_audit()["length"] == 1, "the audit stream survives a reopen"
        assert second.audit()[0]["run_id"] == run_id


def test_the_tool_surface_has_one_definition_per_framework_shape(box):
    names = [tool["name"] for tool in box.tools()]
    assert names == [tool["name"] for tool in TOOLS]
    for style, key in (("openai", "parameters"), ("anthropic", "parameters"), ("mcp", "inputSchema")):
        tools = box.tools(style=style)
        assert [tool["name"] for tool in tools] == names
        assert all(key in tool and "description" in tool for tool in tools)
    with pytest.raises(SandboxError):
        box.tools(style="langchain")


def test_every_advertised_tool_is_dispatchable(box):
    assert box.dispatch("write_file", {"path": "/a.txt", "content": "hello"}).startswith("wrote 5 bytes")
    assert box.dispatch("read_file", {"path": "/a.txt"}) == "hello"
    assert "file" in box.dispatch("list_files", {"path": "/"})
    assert box.dispatch("make_directory", {"path": "/d/e"}) == "created /d/e"
    assert box.dispatch("delete_file", {"path": "/a.txt"}) == "deleted /a.txt"
    output = box.dispatch("run_script", {"source": 'print("from vscript");'})
    assert "from vscript" in output
    assert box.failures == 0, box.audit(status="failure")


def test_dispatch_always_returns_a_string(box):
    for name, arguments in (("nope", {}), ("write_file", {"path": "/x"}), ("read_file", {"path": "/missing"})):
        result = box.dispatch(name, arguments)
        assert isinstance(result, str) and result
    assert box.failures == 3


def test_paths_cannot_escape_the_sandbox(box):
    for path in ("../outside.txt", "/a/../../outside.txt", "..\\outside.txt"):
        assert "may not escape" in box.dispatch("write_file", {"path": path, "content": "x"})
    assert not box.exists("/outside.txt")


def test_a_windows_looking_path_stays_inside_the_image(box):
    """``C:\\Windows\\x`` is a directory in the sandbox, never the host path."""
    box.dispatch("write_file", {"path": r"C:\Windows\evil.txt", "content": "x"})
    assert box.read_text("/C:/Windows/evil.txt") == "x"


def test_empty_and_nul_paths_are_refused(box):
    for path in ("", "   ", "/a\x00b"):
        assert not box.call("read_file", {"path": path}).ok


def test_container_bookkeeping_is_hidden_and_refused(box):
    for path in ("/.system/manifest.json", "/.system/wal.jsonl", "/.vectors", "/.logs", "/.vector_disk.json"):
        result = box.call("read_file", {"path": path})
        assert not result.ok and "bookkeeping" in result.content
    listing = box.dispatch("list_files", {"path": "/", "recursive": True})
    for hidden in ("/.system", "/.vectors", "/.logs", "/.vector_disk.json", "/.log_disk.json"):
        assert hidden not in listing
    assert box.exists("/.system/manifest.json") is False


def test_a_read_only_sandbox_refuses_writes_and_hides_the_tools(tmp_path):
    with AgentSandbox.create(str(tmp_path / "ro.vdisk"), read_only=True) as box:
        names = [tool["name"] for tool in box.tools()]
        assert "write_file" not in names and "delete_file" not in names and "run_script" not in names
        assert names == ["read_file", "list_files"]
        assert not box.call("write_file", {"path": "/x", "content": "y"}).ok
        # The refusal is enforced by the capability layer, not only by the tool list.
        with pytest.raises(PermissionError):
            box.write("/direct.txt", "y")
        with pytest.raises(CapabilityError):
            box.run('import std.fs as fs; fs.write(sandbox, "/x", "y");')


def test_deletion_can_be_disabled_without_making_the_sandbox_read_only(tmp_path):
    with AgentSandbox.create(str(tmp_path / "nodelete.vdisk"), allow_delete=False) as box:
        box.write("/keep.txt", "x")
        assert "delete_file" not in [tool["name"] for tool in box.tools()]
        assert not box.call("delete_file", {"path": "/keep.txt"}).ok
        assert box.exists("/keep.txt")


def test_every_call_is_audited_with_its_arguments_and_outcome(box):
    box.dispatch("write_file", {"path": "/a.txt", "content": "hello"})
    box.dispatch("read_file", {"path": "/nope.txt"})
    box.dispatch("nope", {})
    rows = box.audit()
    assert [row["metrics"]["tool"] for row in rows] == ["write_file", "read_file", "nope"]
    assert [row["status"] for row in rows] == ["success", "failure", "failure"]
    assert rows[0]["metrics"]["arguments"] == {"path": "/a.txt", "content": "hello"}
    assert rows[1]["error"]["type"] == "SandboxError"
    assert all(row["run_id"] == box.run_id for row in rows)
    assert rows[0]["capability_summary"]["permissions"] == ["delete", "read", "write"]
    assert [row["metrics"]["tool"] for row in box.audit(status="failure")] == ["read_file", "nope"]
    assert [row["metrics"]["tool"] for row in box.audit(tool="nope")] == ["nope"]


def test_the_audit_chain_verifies_and_detects_a_foreign_row(box):
    box.dispatch("write_file", {"path": "/a.txt", "content": "x"})
    report = box.verify_audit()
    assert report["ok"] is True and report["length"] == 1
    assert box.audit()[0]["prev_hash"] and box.audit()[0]["hash"]
    # Append a row that did not go through the sink: the chain must notice.
    from pyvdisk.logging_core import LogEvent
    box.disk.logs.append(AUDIT_STREAM, LogEvent(1, "INFO", "attacker", DataDiskAuditSink.MESSAGE,
                                                fields={"tool": "forged", "hash": "0" * 64}))
    broken = box.verify_audit()
    assert broken["ok"] is False


def test_retention_keeps_the_chain_verifiable(tmp_path):
    """Retention drops rows; the chain anchor must let verify() resume past the gap."""
    path = str(tmp_path / "retain.vdisk")
    DataDisk.create(path, 32 << 20)
    with DataDisk(path) as disk:
        # Small segments so rows can actually age out; the sandbox reuses this stream.
        disk.logs.create_stream(AUDIT_STREAM, segment_events=2, max_events=2)
    with AgentSandbox.open(path) as box:
        for index in range(8):
            box.dispatch("write_file", {"path": f"/f{index}.txt", "content": str(index)})
        before = len(box.audit())
        result = box.retain_audit()
        assert result["dropped"] >= 1
        assert len(box.audit()) < before
        assert box.verify_audit()["ok"] is True


def test_scripts_are_confined_to_the_sandbox(box):
    script = (
        'import std.fs as fs;\n'
        'fs.write(sandbox, "/from-script.txt", "written by a script");\n'
        'print("script read:", fs.read_text(sandbox, "/from-script.txt"));\n'
    )
    output = box.dispatch("run_script", {"source": script})
    assert "script read: written by a script" in output
    assert box.read_text("/from-script.txt") == "written by a script"


def test_scripts_see_the_same_root_as_the_python_verbs(box):
    """Both doors must agree: no hidden paths leak through the script door."""
    box.write("/report.md", "hi")
    listing = box.dispatch("run_script", {"source": 'import std.fs as fs; print(fs.listdir(sandbox, "/"));'})
    assert "report.md" in listing
    for hidden in (".system", ".vectors", ".logs", ".vector_disk.json", ".log_disk.json"):
        assert hidden not in listing, f"{hidden} leaked through listdir"
    walked = box.dispatch("run_script", {"source": 'import std.fs as fs; print(fs.walk(sandbox, "/"));'})
    assert ".system" not in walked and ".logs" not in walked
    globbed = box.dispatch("run_script", {"source": 'import std.fs as fs; print(fs.glob(sandbox, "/*"));'})
    assert "/report.md" in globbed and "/.system" not in globbed


def test_scripts_cannot_touch_container_bookkeeping(box):
    for source in ('import std.fs as fs; print(fs.read_text(sandbox, "/.system/manifest.json"));',
                   'import std.fs as fs; fs.write(sandbox, "/.vector_disk.json", "{}");',
                   'import std.fs as fs; print(fs.listdir(sandbox, "/.vectors"));',
                   'import std.fs as fs; print(fs.exists(sandbox, "/.system/wal.jsonl"));'):
        result = box.call("run_script", {"source": source})
        assert not result.ok and "bookkeeping" in result.content, source


def test_the_script_and_python_doors_share_one_workspace(box):
    """A file written by a script is an ordinary file for every other verb."""
    box.dispatch("run_script", {"source": 'import std.fs as fs; fs.write(sandbox, "/shared.txt", "from script");'})
    assert box.read_text("/shared.txt") == "from script"
    box.write("/from-python.txt", "from python")
    seen = box.dispatch("run_script", {"source": 'import std.fs as fs; print(fs.read_text(sandbox, "/from-python.txt"));'})
    assert "from python" in seen


def test_scripts_cannot_reach_the_host_by_default(box):
    for source in ('import std.host as host; print(host.read("/etc/passwd"));',
                   'import std.host as host; host.write("/tmp/pyvdisk-escape", "x"); print("wrote");'):
        result = box.call("run_script", {"source": source})
        assert not result.ok and "未授权" in result.content


def test_host_roots_are_opt_in(tmp_path):
    allowed = tmp_path / "shared"
    allowed.mkdir()
    (allowed / "input.txt").write_text("from the host", encoding="utf-8")
    with AgentSandbox.create(str(tmp_path / "host.vdisk"), host_read_roots=[str(allowed)]) as box:
        result = box.call("run_script", {
            "source": f'import std.host as host; print(host.read("{allowed}/input.txt"));',
        })
        assert result.ok and "from the host" in result.content


def test_script_output_is_bounded_so_a_script_cannot_flood_the_context(tmp_path):
    with AgentSandbox.create(str(tmp_path / "loud.vdisk"), script_output_bytes=512) as box:
        result = box.call("run_script", {"source": 'let i = 0; while i < 5000 { print("x".repeat(200)); i = i + 1; }'})
        assert not result.ok
        assert len(result.content) < 1000


def test_a_script_timeout_is_a_failed_call_not_a_hang(tmp_path):
    with AgentSandbox.create(str(tmp_path / "slow.vdisk")) as box:
        result = box.call("run_script", {"source": 'let i = 0; while true { i = i + 1; }', "args": {}})
        assert not result.ok
        assert "超时" in result.content or "ResourceLimit" in result.content


def test_stats_reports_the_tool_set_and_the_call_counts(box):
    box.write("/a.txt", "x")  # a direct verb: not a tool call, so not counted
    box.call("read_file", {"path": "/missing"})
    stats = box.stats()
    assert stats["name"] == "sandbox"
    assert stats["calls"] == 1 and stats["failures"] == 1
    assert "run_script" in stats["tools"]
    assert stats["disk"]["total_bytes"] > 0
    json.dumps(stats)  # must stay JSON-serialisable for logs and dashboards


def test_a_sandbox_closes_its_disk(box):
    box.close()
    assert box.disk.mounted is False
