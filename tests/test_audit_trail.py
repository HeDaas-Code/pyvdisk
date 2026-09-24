"""Issue #1 B4: the audit trail could only be written to, never read from.

It had no query, no retention and no way to tell whether a record had been edited
after the fact. These tests pin the read side, the retention semantics (including
what happens to the chain when rows are dropped) and the tamper evidence -- both
what it does detect and what it deliberately does not claim.
"""
from __future__ import annotations

import json
import time

import pytest

from pyvdisk import DataDisk
from pyvdisk.infrastructure.checkpoint import CheckpointStore
from pyvdisk.log_disk import LOG_ROOT
from pyvdisk.vscript.audit import (
    GENESIS,
    AuditRecord,
    CheckpointAuditSink,
    DataDiskAuditSink,
    chain_head,
    chain_rows,
    query_rows,
    retain_rows,
    row_hash,
    row_timestamp,
    stamp_row,
    verify_chain,
)


def _record(index=0, *, run_id=None, status="ok", when=None, task_id=None):
    moment = time.time() if when is None else when
    return AuditRecord(
        run_id=run_id if run_id is not None else f"run-{index}",
        script_hash="script",
        policy_hash="policy",
        status=status,
        metrics={"steps": index},
        started_at=moment,
        finished_at=moment,
        task_id=task_id,
    )


def _rows(count, *, status="ok"):
    return [r.to_dict() for r in (_record(i, status=status) for i in range(count))]


# ------------------------------------------------------------------ chain helpers
def test_stamped_rows_form_a_verifiable_chain():
    rows = chain_rows(_rows(4))
    report = verify_chain(rows)
    assert report["ok"] is True and report["length"] == 4
    assert report["broken_at"] is None and report["reason"] is None
    assert rows[0]["prev_hash"] == GENESIS
    assert report["head"] == rows[-1]["hash"]


def test_the_digest_ignores_key_order_and_its_own_hash():
    row = {"run_id": "r", "status": "ok"}
    assert row_hash(row) == row_hash({"status": "ok", "run_id": "r"})
    stamped = stamp_row(row)
    assert row_hash(stamped) == stamped["hash"]
    assert row_hash({**stamped, "hash": "nonsense"}) == stamped["hash"]


def test_editing_a_row_is_detected():
    rows = chain_rows(_rows(3))
    rows[1]["status"] = "tampered"
    report = verify_chain(rows)
    assert report["ok"] is False
    assert report["broken_at"] == 1
    assert report["reason"] == "row content changed"


def test_removing_a_row_breaks_the_link():
    rows = chain_rows(_rows(3))
    del rows[1]
    report = verify_chain(rows)
    assert report["ok"] is False and report["broken_at"] == 1
    assert report["reason"] == "prev_hash does not link"


def test_an_unchained_row_is_reported_not_ignored():
    rows = _rows(2)
    report = verify_chain(rows)
    assert report["ok"] is False and report["reason"] == "row is not chained"
    assert verify_chain(chain_rows(rows))["ok"] is True


def test_verification_can_resume_from_an_anchor():
    rows = chain_rows(_rows(3))
    anchor = rows[1]["hash"]
    report = verify_chain(rows[2:], anchor)
    assert report["ok"] is True and report["length"] == 1
    assert verify_chain(rows[2:])["ok"] is False      # without the anchor it cannot link


def test_chain_head_points_at_the_next_link():
    assert chain_head([]) == GENESIS
    assert chain_head([], "abc") == "abc"
    rows = chain_rows(_rows(2))
    assert chain_head(rows) == rows[-1]["hash"]
    assert chain_head([{"run_id": "unchained"}], "abc") == "abc"


def test_a_rewritten_chain_still_verifies_but_the_head_changes():
    """What the chain does not detect, and why head() exists.

    An editor with write access can re-stamp every row. The chain then verifies;
    only a head digest pinned elsewhere shows that it was rewritten.
    """
    rows = chain_rows(_rows(2))
    original_head = verify_chain(rows)["head"]
    rows[0]["status"] = "tampered"
    rewritten = chain_rows(rows)
    assert verify_chain(rewritten)["ok"] is True
    assert verify_chain(rewritten)["head"] != original_head


# ------------------------------------------------------------------ query and retention
def test_query_filters_by_every_field():
    rows = _rows(6)
    rows[1]["status"] = "failed"
    rows[2]["task_id"] = "task-2"
    assert [r["run_id"] for r in query_rows(rows, status="failed")] == ["run-1"]
    assert [r["run_id"] for r in query_rows(rows, task_id="task-2")] == ["run-2"]
    assert [r["run_id"] for r in query_rows(rows, run_id="run-3")] == ["run-3"]
    assert query_rows(rows, run_id="missing") == []


def test_query_filters_by_time_window():
    base = 1_000_000.0
    rows = [_record(i, when=base + i).to_dict() for i in range(5)]
    assert [r["run_id"] for r in query_rows(rows, since=base + 2)] == ["run-2", "run-3", "run-4"]
    assert [r["run_id"] for r in query_rows(rows, until=base + 1)] == ["run-0", "run-1"]
    assert [r["run_id"] for r in query_rows(rows, since=base + 1, until=base + 3)] == \
        ["run-1", "run-2", "run-3"]


def test_query_limit_keeps_the_oldest_or_the_newest():
    rows = _rows(5)
    assert [r["run_id"] for r in query_rows(rows, limit=2)] == ["run-0", "run-1"]
    assert [r["run_id"] for r in query_rows(rows, limit=2, newest_first=True)] == ["run-4", "run-3"]
    with pytest.raises(ValueError):
        query_rows(rows, limit=-1)


def test_row_timestamp_falls_back_to_started_at():
    assert row_timestamp({"finished_at": 5.0, "started_at": 1.0}) == 5.0
    assert row_timestamp({"started_at": 1.0}) == 1.0
    assert row_timestamp({}) == 0.0
    assert row_timestamp({"finished_at": "not-a-number"}) == 0.0


def test_retention_by_count_keeps_the_newest():
    kept, dropped = retain_rows(_rows(5), max_records=2)
    assert [r["run_id"] for r in kept] == ["run-3", "run-4"]
    assert [r["run_id"] for r in dropped] == ["run-0", "run-1", "run-2"]


def test_retention_by_age_uses_the_record_timestamp():
    now = 1_000_000.0
    rows = [_record(i, when=now - (10 - i)).to_dict() for i in range(5)]   # 6..10s old
    kept, dropped = retain_rows(rows, max_age_seconds=7, now=now)
    assert [r["run_id"] for r in kept] == ["run-3", "run-4"]
    assert [r["run_id"] for r in dropped] == ["run-0", "run-1", "run-2"]


def test_retention_applies_age_before_count():
    now = 1_000_000.0
    rows = [_record(i, when=now - (10 - i)).to_dict() for i in range(5)]
    kept, dropped = retain_rows(rows, max_age_seconds=7, max_records=1, now=now)
    assert [r["run_id"] for r in kept] == ["run-4"]
    assert len(dropped) == 4


def test_retention_rejects_negative_limits():
    for kwargs in ({"max_records": -1}, {"max_age_seconds": -1}):
        with pytest.raises(ValueError):
            retain_rows(_rows(1), **kwargs)


def test_retention_without_a_policy_drops_nothing():
    kept, dropped = retain_rows(_rows(3))
    assert len(kept) == 3 and dropped == []


# ------------------------------------------------------------------ checkpoint sink
@pytest.fixture
def sink(tmp_path):
    return CheckpointAuditSink(CheckpointStore(str(tmp_path / "cp.json")))


def test_the_checkpoint_sink_chains_and_verifies(sink):
    for index in range(4):
        sink.emit(_record(index))
    report = sink.verify()
    assert report["ok"] is True and report["length"] == 4
    assert sink.head() == sink.records()[-1]["hash"]
    assert sink.records()[0]["prev_hash"] == GENESIS


def test_the_checkpoint_sink_queries(sink):
    sink.emit(_record(0, run_id="a"))
    sink.emit(_record(1, run_id="b", status="failed"))
    assert [r["run_id"] for r in sink.query(status="failed")] == ["b"]
    assert [r["run_id"] for r in sink.query(run_id="a")] == ["a"]
    assert len(sink.query(limit=1, newest_first=True)) == 1


def test_the_checkpoint_sink_detects_an_edited_row(sink):
    for index in range(3):
        sink.emit(_record(index))
    rows = [dict(row) for row in sink.records()]
    rows[1]["status"] = "tampered"
    sink.store.set(sink.key, rows)
    report = sink.verify()
    assert report["ok"] is False and report["broken_at"] == 1


def test_retention_keeps_the_chain_verifiable(sink):
    for index in range(5):
        sink.emit(_record(index))
    before = sink.verify()["head"]
    outcome = sink.retain(max_records=2)
    assert outcome["dropped"] == 3 and outcome["kept"] == 2
    assert outcome["anchor"] != GENESIS
    assert sink.verify()["ok"] is True
    # Dropping the oldest rows leaves the newest record's attestation -- the head --
    # exactly as it was; only the anchor moves up to where the chain resumes.
    assert sink.verify()["head"] == before

    sink.emit(_record(9))                    # the chain continues from the retained tail
    assert sink.verify()["ok"] is True and sink.verify()["length"] == 3
    assert sink.verify()["head"] != before


def test_retention_by_age_anchors_the_chain(sink):
    now = time.time()
    for index in range(4):
        sink.emit(_record(index, when=now - (100 - index)))
    outcome = sink.retain(max_age_seconds=98, now=now)
    assert outcome["dropped"] == 2 and outcome["kept"] == 2
    assert sink.verify()["ok"] is True


def test_adopting_an_unchained_log(sink):
    legacy = _rows(3)
    sink.store.set(sink.key, legacy)
    assert sink.verify()["ok"] is False
    assert sink.adopt() == 3
    assert sink.verify()["ok"] is True
    sink.emit(_record(3))
    assert sink.verify()["length"] == 4


def test_chaining_can_be_turned_off(sink, tmp_path):
    plain = CheckpointAuditSink(CheckpointStore(str(tmp_path / "plain.json")), chained=False)
    plain.emit(_record(0))
    assert "hash" not in plain.records()[0]
    assert plain.query(run_id="run-0")


# ------------------------------------------------------------------ datadisk sink
@pytest.fixture
def disk(tmp_path):
    mounted = DataDisk.create(tmp_path / "audit.vdisk", 32 * 1024 * 1024).mount()
    yield mounted
    mounted.close()


def test_the_datadisk_sink_chains_through_the_log(disk):
    sink = DataDiskAuditSink(disk, "audit")
    for index in range(3):
        sink.emit(_record(index))
    report = sink.verify()
    assert report["ok"] is True and report["length"] == 3
    assert len(sink.records()) == 3
    assert sink.records()[0]["run_id"] == "run-0"


def test_the_datadisk_sink_queries_the_stream(disk):
    sink = DataDiskAuditSink(disk, "audit")
    sink.emit(_record(0, run_id="a", status="ok"))
    sink.emit(_record(1, run_id="b", status="failed"))
    assert [r["run_id"] for r in sink.query(status="failed")] == ["b"]
    assert [r["run_id"] for r in sink.query(limit=1, newest_first=True)] == ["b"]


def test_the_datadisk_sink_reuses_an_existing_stream_with_retention(disk):
    disk.logs.create_stream("audit", segment_events=2, max_events=2)
    sink = DataDiskAuditSink(disk, "audit")
    for index in range(6):
        sink.emit(_record(index))
    assert sink.verify()["length"] == 6

    outcome = sink.retain()
    assert outcome["dropped"] == 4 and outcome["kept"] == 2
    assert outcome["anchor"] not in (None, GENESIS)
    # The dropped segment took its rows with it; the anchor explains the gap.
    assert sink.verify()["ok"] is True and sink.verify()["length"] == 2

    sink.emit(_record(9))
    assert sink.verify()["ok"] is True and sink.verify()["length"] == 3


def test_the_datadisk_sink_detects_an_edited_record(disk):
    sink = DataDiskAuditSink(disk, "audit")
    for index in range(3):
        sink.emit(_record(index))
    stream_dir = disk.vfs.listdir(LOG_ROOT)[0]
    segments = f"{LOG_ROOT}/{stream_dir}/segments"
    name = disk.vfs.listdir(segments)[0]
    raw = disk.vfs.read_file(f"{segments}/{name}").decode("utf-8")
    lines = raw.splitlines()
    first = json.loads(lines[0])
    first["fields"]["status"] = "tampered"
    lines[0] = json.dumps(first)
    disk.vfs.write_file(f"{segments}/{name}", ("\n".join(lines) + "\n").encode("utf-8"))

    report = sink.verify()
    assert report["ok"] is False
    assert report["broken_at"] == 0
    assert report["reason"] == "row content changed"


def test_the_datadisk_sink_can_turn_chaining_off(disk):
    sink = DataDiskAuditSink(disk, "audit", chained=False)
    sink.emit(_record(0))
    assert "hash" not in sink.records()[0]
    assert sink.verify()["ok"] is False       # unchained rows are reported, not trusted
    assert sink.query(run_id="run-0")
