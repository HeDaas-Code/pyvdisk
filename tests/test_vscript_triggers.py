"""Issue #1 D: cron and the trigger registry had no tests at all.

Writing these found a real defect: ``_log_events`` treated the log's ``event_id``
as a watermark, but ``LogEvent.event_id`` is a random uuid4 hex, so it dropped
roughly half of the events that should have been delivered. The cursor tests below
pin the corrected behaviour.
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path

import pytest

from pyvdisk.vscript.checkpoint import CheckpointStore
from pyvdisk.vscript.triggers import (
    Daemon,
    SchedulerDaemon,
    Trigger,
    TriggerRegistry,
    event_position,
    is_newer,
    register_file_trigger,
    register_log_trigger,
)


class _Event:
    """Stand-in for LogEvent: random id by default, monotonic sequence."""

    def __init__(self, sequence, event_id=None, message=""):
        self.sequence = sequence
        self.event_id = event_id or uuid.uuid4().hex
        self.message = message


class _Source:
    def __init__(self, events=()):
        self.events = list(events)
        self.queries = []

    def query(self, stream, levels=None, loggers=None):
        self.queries.append((stream, levels, loggers))
        return list(self.events)


def _registry(tmp_path):
    return TriggerRegistry(tmp_path / "triggers.json")


def _file_daemon(tmp_path, pattern="*.txt", events=("create", "modify", "delete")):
    registry = _registry(tmp_path)
    registry.register_file("watch", pattern, events)
    return SchedulerDaemon(registry, str(tmp_path / "cp.json"), root=tmp_path), registry


# ------------------------------------------------------------------ registry
def test_registry_round_trips_through_disk(tmp_path):
    registry = _registry(tmp_path)
    registry.register_file("watcher", "*.txt")
    registry.register_log("errors", "app", levels=("ERROR",), logger="svc")
    again = _registry(tmp_path)
    by_name = {t.name: t for t in again.list()}
    assert set(by_name) == {"watcher", "errors"}
    assert by_name["watcher"].kind == "file" and by_name["watcher"].pattern == "*.txt"
    assert by_name["watcher"].events == ("create", "modify", "delete")
    assert by_name["errors"].kind == "log" and by_name["errors"].stream == "app"
    assert by_name["errors"].levels == ("ERROR",) and by_name["errors"].logger == "svc"


def test_registry_rejects_bad_triggers(tmp_path):
    registry = _registry(tmp_path)
    for bad in (
        Trigger("", "file", pattern="*.txt"),
        Trigger("x", "socket"),
        Trigger("x", "file", pattern=""),   # would raise out of the poll loop
        Trigger("x", "log", stream=""),
        "not-a-trigger",
    ):
        with pytest.raises(ValueError):
            registry.register(bad)
    assert registry.list() == ()


def test_remove_is_persisted(tmp_path):
    registry = _registry(tmp_path)
    registry.register_file("a", "*.txt")
    registry.register_file("b", "*.md")
    registry.remove("a")
    assert [t.name for t in _registry(tmp_path).list()] == ["b"]
    registry.remove("gone")  # removing something absent is not an error
    assert [t.name for t in registry.list()] == ["b"]


def test_registry_survives_a_corrupt_file_shape(tmp_path):
    path = tmp_path / "triggers.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(ValueError):
        TriggerRegistry(path)


def test_module_level_helpers_register(tmp_path):
    registry = _registry(tmp_path)
    register_file_trigger(registry, "f", "*.log", ("create",))
    register_log_trigger(registry, "l", "app", ("WARN",), "svc")
    by_name = {t.name: t for t in registry.list()}
    assert by_name["f"].events == ("create",)
    assert by_name["l"].levels == ("WARN",) and by_name["l"].logger == "svc"


def test_daemon_alias_and_coercion(tmp_path):
    assert Daemon is SchedulerDaemon
    daemon = SchedulerDaemon(str(tmp_path / "t.json"), str(tmp_path / "cp.json"), root=tmp_path)
    assert isinstance(daemon.registry, TriggerRegistry)
    assert isinstance(daemon.checkpoint, CheckpointStore)


# ------------------------------------------------------------------ file triggers
def test_file_events_report_create_modify_and_delete(tmp_path):
    daemon, _ = _file_daemon(tmp_path)
    seen = []
    daemon.poll_once({"watch": seen.append})  # empty tree first

    (tmp_path / "a.txt").write_text("one", encoding="utf-8")
    daemon.poll_once({"watch": seen.append})
    assert [e["event"] for e in seen] == ["create"]

    (tmp_path / "a.txt").write_text("two", encoding="utf-8")
    daemon.poll_once({"watch": seen.append})
    assert [e["event"] for e in seen] == ["create", "modify"]

    (tmp_path / "a.txt").unlink()
    daemon.poll_once({"watch": seen.append})
    assert [e["event"] for e in seen] == ["create", "modify", "delete"]
    assert seen[0]["path"] == "a.txt"


def test_file_trigger_ignores_events_it_did_not_subscribe_to(tmp_path):
    daemon, _ = _file_daemon(tmp_path, events=("create",))
    seen = []
    daemon.poll_once({"watch": seen.append})
    (tmp_path / "a.txt").write_text("one", encoding="utf-8")
    daemon.poll_once({"watch": seen.append})
    (tmp_path / "a.txt").write_text("changed", encoding="utf-8")
    daemon.poll_once({"watch": seen.append})
    assert [e["event"] for e in seen] == ["create"]


def test_file_trigger_ignores_files_outside_its_pattern(tmp_path):
    daemon, _ = _file_daemon(tmp_path, pattern="*.txt")
    seen = []
    daemon.poll_once({"watch": seen.append})
    (tmp_path / "notes.md").write_text("x", encoding="utf-8")
    assert daemon.poll_once({"watch": seen.append}) == 0
    assert seen == []


def test_poll_once_counts_what_it_delivered(tmp_path):
    daemon, _ = _file_daemon(tmp_path)
    daemon.poll_once({"watch": lambda e: None})
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    (tmp_path / "b.txt").write_text("2", encoding="utf-8")
    assert daemon.poll_once({"watch": lambda e: None}) == 2


# ------------------------------------------------------------------ log triggers
def _log_daemon(tmp_path, events):
    registry = _registry(tmp_path)
    registry.register_log("errors", "app")
    source = _Source(events)
    return SchedulerDaemon(registry, str(tmp_path / "cp.json"), root=tmp_path,
                           log_sources={"errors": source}), source


def test_log_trigger_delivers_everything_after_the_watermark(tmp_path):
    """Regression: random uuid ids cannot be compared as text.

    Comparing ids dropped events whose id happened to sort before the stored one --
    about half of them. The monotonic sequence is the cursor that means "after".
    """
    daemon, _ = _log_daemon(tmp_path, [_Event(i, message=f"m{i}") for i in range(6)])
    seen = []
    daemon.poll_once({"errors": seen.append})
    assert [e.message for e in seen] == [f"m{i}" for i in range(6)]

    # A second poll re-reads the same log and must not repeat itself.
    assert daemon.poll_once({"errors": seen.append}) == 0
    assert len(seen) == 6


def test_log_trigger_resumes_from_the_checkpoint(tmp_path):
    events = [_Event(i) for i in range(3)]
    daemon, source = _log_daemon(tmp_path, events)
    seen = []
    daemon.poll_once({"errors": seen.append})
    assert len(seen) == 3

    source.events.extend([_Event(3), _Event(4)])
    assert daemon.poll_once({"errors": seen.append}) == 2
    assert [e.sequence for e in seen] == [0, 1, 2, 3, 4]


def test_a_failing_handler_is_retried_instead_of_forgotten(tmp_path):
    """The checkpoint is written after the handler, so failure means redelivery."""
    daemon, _ = _log_daemon(tmp_path, [_Event(0), _Event(1)])
    attempts = []

    def boom(event):
        attempts.append(event)
        raise RuntimeError("handler failed")

    with pytest.raises(RuntimeError):
        daemon.poll_once({"errors": boom})
    assert len(attempts) == 1
    with pytest.raises(RuntimeError):
        daemon.poll_once({"errors": boom})
    assert len(attempts) == 2  # same event, not a silently lost one


def test_log_trigger_passes_its_filters_to_the_source(tmp_path):
    daemon, source = _log_daemon(tmp_path, [])
    daemon.registry.register_log("warn", "app", levels=("WARN",), logger="svc")
    daemon.log_sources["warn"] = source
    daemon.poll_once({"errors": lambda e: None, "warn": lambda e: None})
    assert ("app", ["WARN"], ["svc"]) in source.queries


def test_log_trigger_without_a_source_delivers_nothing(tmp_path):
    registry = _registry(tmp_path)
    registry.register_log("errors", "app")
    daemon = SchedulerDaemon(registry, str(tmp_path / "cp.json"), root=tmp_path)
    assert daemon.poll_once({"errors": lambda e: None}) == 0


def test_run_stops_when_the_stop_event_is_set(tmp_path):
    daemon, _ = _file_daemon(tmp_path)
    stop = threading.Event()
    polled = []

    def handler(event):
        polled.append(event)
        stop.set()

    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    daemon.run({"watch": handler}, interval=0.01, stop_event=stop)
    assert len(polled) == 1
    assert stop.is_set()


def test_run_with_a_slow_handler_is_bounded_by_the_stop_event(tmp_path):
    daemon, _ = _file_daemon(tmp_path)
    stop = threading.Event()
    calls = []

    def handler(event):
        calls.append(event)

    timer = threading.Timer(0.05, stop.set)
    timer.start()
    try:
        daemon.run({"watch": handler}, interval=0.01, stop_event=stop)
    finally:
        timer.cancel()
    assert calls == []


# ------------------------------------------------------------------ cursors
def test_event_position_prefers_the_sequence():
    assert event_position(_Event(7)) == 7
    assert event_position(_Event(None, event_id="abc")) == "abc"


def test_is_newer_compares_numbers_when_it_can():
    assert is_newer(3, "2") is True
    assert is_newer(2, "2") is False
    assert is_newer(1, "2") is False
    # Without sequences only an exact repeat counts as seen.
    assert is_newer("abc", "abc") is False
    assert is_newer("xyz", "abc") is True
