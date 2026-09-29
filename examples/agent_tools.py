#!/usr/bin/env python3
"""Wire AgentSandbox into an agent loop -- offline, no API key, no network.

    python examples/agent_tools.py [workdir]

The "model" here is a scripted list of tool calls, so this runs anywhere. The
loop is exactly the one you write against a real framework: ask the model, run
every tool call it asks for, feed the results back, repeat until it stops asking.
Swap ``scripted_model`` for an OpenAI-compatible client and nothing else changes --
``box.tools()`` and ``box.dispatch()`` are the whole integration surface.

Note the last scripted call: the model asks to read ``/etc/passwd`` and gets a
refusal, which is fed back like any other tool result. That is the point of
running an agent against a sandbox rather than a directory.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile

if importlib.util.find_spec("pyvdisk") is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyvdisk import AgentSandbox  # noqa: E402 - the path fix has to run first

#: What a model would have produced. Each entry is one assistant turn; an entry
#: with several calls reproduces a model asking for more than one tool at once.
SCRIPTED_TURNS = [
    {"tool": "list_files", "arguments": {"path": "/"}},
    {"tool": "write_file", "arguments": {
        "path": "/report.md",
        "content": "# Findings\n\nThe sandbox works.\n",
    }},
    {"tool": "run_script", "arguments": {"source": (
        'import std.fs as fs;\n'
        'let names = fs.listdir(sandbox, "/");\n'
        'print("files:", names);\n'
        'fs.write(sandbox, "/from-script.txt", "written inside the sandbox");\n'
    )}},
    {"tool": "read_file", "arguments": {"path": "/report.md"}},
    {"tool": "read_file", "arguments": {"path": "/etc/passwd"}},   # refused
    # Two tools in one turn: the loop must answer each with its own call id.
    {"calls": [
        {"tool": "read_file", "arguments": {"path": "/from-script.txt"}},
        {"tool": "list_files", "arguments": {"path": "/", "recursive": True}},
    ]},
]


class _Message:
    """The assistant message shape the OpenAI client returns."""

    def __init__(self, calls):
        self.tool_calls = [_ToolCall(f"call_{index}", tool, arguments)
                           for index, (tool, arguments) in enumerate(calls)]


class _ToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = type("Function", (), {"name": name,
                                              "arguments": json.dumps(arguments, ensure_ascii=False)})()


def scripted_model(messages):
    """Stand-in for one chat completion: returns the next assistant message.

    Returns an empty-tool_calls message once the script runs out, which is how a
    real model signals "I am done" -- the loop below treats it identically.
    """
    # Assistant turns are objects, tool results are plain dicts; count the latter.
    asked = sum(1 for message in messages
                if isinstance(message, dict) and message.get("role") == "tool")
    turn = SCRIPTED_TURNS[asked] if asked < len(SCRIPTED_TURNS) else None
    if turn is None:
        return _Message([])
    calls = [(tool["tool"], tool["arguments"]) for tool in turn.get("calls", [turn])]
    return _Message(calls)


def main(argv):
    work = argv[1] if len(argv) > 1 else tempfile.mkdtemp(prefix="pyvdisk-agent-")
    os.makedirs(work, exist_ok=True)

    with AgentSandbox.create(os.path.join(work, "agent.vdisk"), size_bytes=32 << 20) as box:
        print("tools offered to the model:", ", ".join(tool["name"] for tool in box.tools()))
        print("json schema of one tool:", json.dumps(box.tools()[0], ensure_ascii=False)[:120], "...\n")

        messages = [{"role": "user", "content": "Summarise the workspace and write /report.md"}]
        step = 0
        while step < 12:
            # Identical to the README demo: ask, append the assistant message, run
            # every call it asked for, feed each result back by its own call id.
            message = scripted_model(messages)
            messages.append(message)
            if not message.tool_calls:
                break
            for call in message.tool_calls:
                step += 1
                arguments = json.loads(call.function.arguments)
                result = box.dispatch(call.function.name, arguments)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
                print(f"[{step}] {call.function.name}({call.function.arguments[:60]})")
                print("     ->", result.replace("\n", "\n        "))

        print("\nfinal /report.md:", repr(box.read_text("/report.md")))
        report = box.verify_audit()
        print(f"audit: {report['length']} chained records, chain ok = {report['ok']}")
        print("refusals recorded:",
              [row["metrics"]["tool"] for row in box.audit(status="failure")])
        print("\nEvery call above is durable, hash-chained and replayable: reopen",
              os.path.join(work, "agent.vdisk"), "to see it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
