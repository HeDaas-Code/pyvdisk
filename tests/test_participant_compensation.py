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


def _kill(disk):
    """Simulate process death by releasing the image without DataDisk shutdown.

    ``DataDisk.close()`` settles and truncates the log, so using it after a simulated
    crash would perform the recovery this module exists to test.
    """
    disk.vfs.close()


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
    _kill(disk)

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
    _kill(disk)

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
    _kill(disk)

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
    _kill(disk)

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
    _kill(disk)

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
    _kill(disk)

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
    _kill(disk)

    # No factory registered: recovery still compensates what it owns and stays healthy.
    reopened = DataDisk(path).mount()
    try:
        assert reopened.recovery_report()["participants"] == []
        assert reopened.get_metadata("answer") is None
    finally:
        reopened.close()


# ---------------------------------------------------------------- A3: live abort
# ARCHITECTURE §8.6 promises participants are told to compensate via
# abort(txid, intents). Mount recovery did that; aborting a live transaction did not,
# so an in-process abort left participant side effects behind.
def test_abort_notifies_enlisted_participants_in_process(tmp_path):
    disk = _new(tmp_path / "abort.vdisk")
    try:
        participant = RecordingParticipant()
        tx = disk.transaction().set("answer", 42).enlist(participant, {"op": "upsert", "id": "a"})
        tx.abort()
        assert participant.aborted == 1
        assert participant.ledger == [("abort", tx.txid, ({"op": "upsert", "id": "a"},))]
        assert disk.get_metadata("answer") is None
    finally:
        disk.close()


def test_an_exception_in_the_transaction_block_compensates_participants(tmp_path):
    disk = _new(tmp_path / "context.vdisk")
    try:
        participant = RecordingParticipant()
        with pytest.raises(RuntimeError):
            with disk.transaction() as tx:
                tx.set("answer", 42).enlist(participant, {"op": "set"})
                raise RuntimeError("caller failed")
        assert participant.aborted == 1
        assert disk.get_metadata("answer") is None
    finally:
        disk.close()


def test_a_participant_enlisted_without_an_intent_is_still_told(tmp_path):
    disk = _new(tmp_path / "no-intent.vdisk")
    try:
        participant = RecordingParticipant()
        tx = disk.transaction().enlist(participant)
        tx.abort()
        assert participant.ledger == [("abort", tx.txid, ())]
    finally:
        disk.close()


def test_abort_persists_intents_so_recovery_can_compensate_too(tmp_path):
    """A crash right after a live abort must not lose the participant's intent."""
    path = tmp_path / "abort-crash.vdisk"
    disk = _new(path)
    participant = RecordingParticipant()
    tx = disk.transaction().set("answer", 42).enlist(participant, {"op": "set"})
    tx.abort()
    assert participant.aborted == 1
    txid = tx.txid
    _kill(disk)

    replayed = []
    reopened = DataDisk(path)
    reopened.register_recovery_participant("RecordingParticipant", lambda d: RecordingParticipant(replayed))
    reopened.mount()
    try:
        assert replayed == [("abort", txid, ({"op": "set"},))]
        assert reopened.get_metadata("answer") is None
    finally:
        reopened.close()


def test_abort_dispatches_in_reverse_order_and_survives_a_failure(tmp_path):
    disk = _new(tmp_path / "reverse.vdisk")
    order = []

    class Marked(RecordingParticipant):
        def __init__(self, name, ledger, fail=False):
            super().__init__(ledger)
            self.name, self.fail = name, fail

        def abort(self, txid, intents):
            order.append(self.name)
            super().abort(txid, intents)
            if self.fail:
                raise RuntimeError(f"{self.name} cannot compensate")

    try:
        ledger = []
        first = Marked("first", ledger)
        second = Marked("second", ledger, fail=True)
        third = Marked("third", ledger)
        tx = (disk.transaction().enlist(first, {"n": 1}).enlist(second, {"n": 2})
              .enlist(third, {"n": 3}))
        tx.abort()                       # a failing participant must not abort the abort
        assert order == ["third", "second", "first"]
        assert [entry[0] for entry in ledger] == ["abort", "abort", "abort"]
        assert ({"n": 1},) in [entry[2] for entry in ledger]
    finally:
        disk.close()


def test_abort_notifies_participants_only_once(tmp_path):
    disk = _new(tmp_path / "twice.vdisk")
    try:
        participant = RecordingParticipant()
        tx = disk.transaction().enlist(participant, {"op": "set"})
        tx.abort()
        tx.abort()
        assert participant.aborted == 1
    finally:
        disk.close()
