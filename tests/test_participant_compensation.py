"""Issue #1 A2: participant side effects are compensated after a crash.

The canonical crash window is: every participant has acted (filesystem, vector and
log namespaces, plus any enlisted participant), but the durable ``commit`` record
has not been written yet. Metadata is rolled back on the next mount, and these
tests pin that the participant effects are rolled back with it from the durable
write-ahead compensation log -- not left half-applied.
"""
from __future__ import annotations

import pytest

from pyvdisk import DataDisk, LogEvent
from pyvdisk.infrastructure import TransactionParticipant


class Crash(BaseException):
    """Process-loss simulation: deliberately bypasses transaction exception cleanup."""


def _new(path):
    return DataDisk.create(path, 32 * 1024 * 1024).mount()


class RecordingParticipant(TransactionParticipant):
    def __init__(self, ledger=None):
        self.ledger = ledger if ledger is not None else []
        self.committed = 0
        self.aborted = 0

    def commit(self, txid, intents):
        self.committed += 1
        self.ledger.append(("commit", txid, tuple(intents)))

    def abort(self, txid, intents):
        self.aborted += 1
        self.ledger.append(("abort", txid, tuple(intents)))


def _crash_after_participant_commit(participant):
    """Die right after the participant has acted, before the commit record."""
    original = participant.commit
    fired = False

    def commit(*args):
        nonlocal fired
        original(*args)
        if not fired:
            fired = True
            raise Crash()

    participant.commit = commit


def _crash_before_commit_record(disk):
    """Die after ``apply`` is durable and the namespaces have acted."""
    original = disk._append_metadata_wal
    fired = False

    def append(record):
        nonlocal fired
        original(record)
        if not fired and record.get("kind") == "apply":
            fired = True
            raise Crash()

    disk._append_metadata_wal = append


def test_filesystem_effects_are_compensated_after_crash(tmp_path):
    path = tmp_path / "fs.vdisk"
    disk = _new(path)
    disk.fs.write_file("/keep.txt", b"original")
    participant = RecordingParticipant()
    _crash_after_participant_commit(participant)
    with pytest.raises(Crash):
        with disk.transaction() as tx:
            tx.set("answer", 42).enlist(participant, {"op": "set"})
            disk.fs.write_file("/keep.txt", b"changed")
            disk.fs.write_file("/new.txt", b"fresh")
    txid = tx.txid

    # The crash bypassed cleanup, so the side effects are live and uncompensated.
    assert participant.committed == 1
    assert disk.fs.read_file("/keep.txt") == b"changed"
    assert disk.fs.exists("/new.txt") is True
    disk.close()

    reopened = DataDisk(path).mount()
    try:
        assert reopened.get_metadata("answer") is None
        assert reopened.fs.read_file("/keep.txt") == b"original"
        assert reopened.fs.exists("/new.txt") is False
        assert reopened.recovery_report()["compensated"] == [txid]
    finally:
        reopened.close()

    # Mount recovery is idempotent: a second mount changes nothing further.
    again = DataDisk(path).mount()
    try:
        assert again.get_metadata("answer") is None
        assert again.fs.read_file("/keep.txt") == b"original"
        assert again.recovery_report()["compensated"] == []
    finally:
        again.close()


def test_directory_and_removal_effects_are_undone_from_the_log(tmp_path):
    path = tmp_path / "fs2.vdisk"
    disk = _new(path)
    disk.fs.makedirs("/dir/sub")
    disk.fs.write_file("/dir/sub/gone.txt", b"keepme")
    _crash_before_commit_record(disk)
    with pytest.raises(Crash):
        with disk.transaction() as tx:
            tx.set("answer", 42)
            disk.fs.remove("/dir/sub/gone.txt")
            disk.fs.makedirs("/fresh/deep")
            disk.fs.write_file("/fresh/deep/new.txt", b"new")
    assert disk.fs.exists("/dir/sub/gone.txt") is False
    disk.close()

    reopened = DataDisk(path).mount()
    try:
        assert reopened.get_metadata("answer") is None
        assert reopened.fs.read_file("/dir/sub/gone.txt") == b"keepme"
        assert reopened.fs.exists("/fresh/deep/new.txt") is False
    finally:
        reopened.close()


def test_committed_transaction_effects_survive_recovery(tmp_path):
    path = tmp_path / "ok.vdisk"
    disk = _new(path)
    disk.fs.write_file("/keep.txt", b"original")
    with disk.transaction() as tx:
        tx.set("answer", 42)
        disk.fs.write_file("/keep.txt", b"committed")
        disk.fs.write_file("/new.txt", b"new")
    txid = tx.txid
    disk.close()

    reopened = DataDisk(path).mount()
    try:
        # A committed transaction is redone, never compensated.
        assert reopened.get_metadata("answer") == 42
        assert reopened.fs.read_file("/keep.txt") == b"committed"
        assert reopened.fs.read_file("/new.txt") == b"new"
        assert txid in reopened.recovery_report()["committed"]
        assert txid not in reopened.recovery_report()["compensated"]
    finally:
        reopened.close()


def test_vector_namespace_effects_are_compensated_after_crash(tmp_path):
    path = tmp_path / "vector.vdisk"
    disk = _new(path)
    disk.vector.create_collection("items", 2, max_elements=8)
    disk.vector.upsert("items", "baseline", [0.5, 0.5], {"v": 0})
    _crash_before_commit_record(disk)
    with pytest.raises(Crash):
        with disk.transaction() as tx:
            tx.set("answer", 42)
            disk.vector.upsert("items", "added", [1.0, 0.0], {"v": 1})
    assert disk.vector.get("items", "added") is not None
    disk.close()

    reopened = DataDisk(path).mount()
    try:
        assert reopened.get_metadata("answer") is None
        assert reopened.vector.get("items", "added") is None
        # The pre-transaction record is untouched.
        assert reopened.vector.get("items", "baseline")["metadata"] == {"v": 0}
    finally:
        reopened.close()


def test_log_namespace_effects_are_compensated_after_crash(tmp_path):
    path = tmp_path / "log.vdisk"
    disk = _new(path)
    disk.log.create_stream("events")
    disk.log.append("events", LogEvent(1, "INFO", "test", "baseline"))
    _crash_before_commit_record(disk)
    with pytest.raises(Crash):
        with disk.transaction() as tx:
            tx.set("answer", 42)
            disk.log.append("events", LogEvent(2, "INFO", "test", "transient"))
    assert [e.message for e in disk.log.query("events")] == ["baseline", "transient"]
    disk.close()

    reopened = DataDisk(path).mount()
    try:
        assert reopened.get_metadata("answer") is None
        assert [event.message for event in reopened.log.query("events")] == ["baseline"]
    finally:
        reopened.close()


def test_registered_participant_is_compensated_with_its_persisted_intent(tmp_path):
    path = tmp_path / "participant.vdisk"
    disk = _new(path)
    participant = RecordingParticipant()
    tx = disk.transaction().set("answer", 42).enlist(participant, {"op": "upsert", "id": "a"})
    _crash_after_participant_commit(participant)
    with pytest.raises(Crash):
        tx.commit()
    txid = tx.txid
    assert participant.committed == 1
    disk.close()

    reopened = DataDisk(path)
    replayed = []
    reopened.register_recovery_participant("RecordingParticipant", lambda d: RecordingParticipant(replayed))
    reopened.mount()
    try:
        # Recovery rebuilt the participant and compensated it with the intent
        # recovered from the durable log, without the original object existing.
        assert replayed == [("abort", txid, ({"op": "upsert", "id": "a"},))]
        assert reopened.recovery_report()["participants"] == [
            {"txid": txid, "participant": "RecordingParticipant"}
        ]
        assert reopened.get_metadata("answer") is None
    finally:
        reopened.close()


def test_recovery_reports_unknown_participants_without_failing(tmp_path):
    path = tmp_path / "unknown.vdisk"
    disk = _new(path)
    participant = RecordingParticipant()
    tx = disk.transaction().set("answer", 42).enlist(participant, {"op": "set"})
    _crash_after_participant_commit(participant)
    with pytest.raises(Crash):
        tx.commit()
    disk.close()

    # No factory registered: recovery still compensates what it owns and stays healthy.
    reopened = DataDisk(path).mount()
    try:
        assert reopened.recovery_report()["participants"] == []
        assert reopened.get_metadata("answer") is None
    finally:
        reopened.close()
