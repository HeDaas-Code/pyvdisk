"""Crash-injection matrix for the canonical single-image DataDisk protocol."""
from __future__ import annotations

import pytest

from pyvdisk import DataDisk, LogEvent
from pyvdisk.infrastructure import DurableQueue, TransactionParticipant


class Crash(BaseException):
    """Process-loss simulation: deliberately bypasses transaction exception cleanup."""


def _new(path):
    return DataDisk.create(path, 32 * 1024 * 1024).mount()


class RecordingParticipant(TransactionParticipant):
    def __init__(self):
        self.prepared = 0
        self.committed = 0

    def prepare(self, txid, intents):
        self.prepared += 1

    def commit(self, txid, intents):
        self.committed += 1


def _inject(stage, disk, participant):
    """Raise BaseException at each durable protocol boundary."""
    original_append = disk._append_metadata_wal
    original_atomic = disk._atomic_json
    original_prepare = participant.prepare
    original_commit = participant.commit
    fired = False

    def append(record):
        nonlocal fired
        original_append(record)
        if stage == "before prepare" and record["kind"] == "intent" and not fired:
            fired = True; raise Crash()
        if stage == "after prepare" and record["kind"] == "prepare" and not fired:
            fired = True; raise Crash()

    def atomic(path, value):
        nonlocal fired
        original_atomic(path, value)
        if stage == "after metadata publish" and path == disk.METADATA and not fired:
            fired = True; raise Crash()

    def prepare(*args):
        nonlocal fired
        original_prepare(*args)
        if stage == "after prepare callback" and not fired:
            fired = True; raise Crash()

    def commit(*args):
        nonlocal fired
        original_commit(*args)
        if stage == "after participant commit" and not fired:
            fired = True; raise Crash()

    disk._append_metadata_wal = append
    disk._atomic_json = atomic
    participant.prepare = prepare
    participant.commit = commit


@pytest.mark.parametrize("stage", ["before prepare", "after prepare", "after metadata publish"])
def test_metadata_crash_matrix_remount_and_repeated_recovery(tmp_path, stage):
    path = tmp_path / (stage.replace(" ", "_") + ".vdisk")
    disk = _new(path)
    participant = RecordingParticipant()
    tx = disk.transaction().set("answer", 42).enlist(participant, {"op": "set"})
    _inject(stage, disk, participant)
    with pytest.raises(Crash):
        tx.commit()
    disk.close()

    recovered = DataDisk(path).mount()
    assert recovered.get_metadata("answer") is None
    # Mount/recovery is repeatable and does not resurrect the incomplete change.
    recovered.close()
    again = DataDisk(path).mount()
    assert again.get_metadata("answer") is None
    again.close()


def test_after_participant_commit_is_recoverable_and_participant_is_not_replayed(tmp_path):
    path = tmp_path / "participant.vdisk"
    disk = _new(path)
    participant = RecordingParticipant()
    tx = disk.transaction().set("answer", 42).enlist(participant, {"op": "set"})
    _inject("after participant commit", disk, participant)
    with pytest.raises(Crash):
        tx.commit()
    assert participant.committed == 1
    disk.close()
    reopened = DataDisk(path).mount()
    assert reopened.get_metadata("answer") is None
    reopened.close()


def test_vector_generation_log_sequence_and_checkpoint_survive_remount(tmp_path):
    path = tmp_path / "namespaces.vdisk"
    disk = _new(path)
    disk.vector.create_collection("items", 2, max_elements=8)
    disk.vector.upsert("items", "a", [1, 0], {"v": 1})
    disk.log.create_stream("events")
    first = disk.log.append("events", LogEvent(1, "INFO", "test", "one"))
    second = disk.log.append("events", LogEvent(2, "INFO", "test", "two"))
    disk.checkpoints.mark_success("job", first.event_id)
    config = disk.vector.list_collections()[0]
    assert config["generation"] == config["index_generation"] == 1
    assert [first.sequence, second.sequence] == [0, 1]
    disk.close()
    reopened = DataDisk(path).mount()
    config2 = reopened.vector.list_collections()[0]
    assert config2["generation"] == config2["index_generation"] == 1
    assert [e.sequence for e in reopened.log.query("events")] == [0, 1]
    assert reopened.checkpoints.last_event("job") == first.event_id
    reopened.close()


def test_after_queue_result_is_deduplicated_across_remount_and_recovery(tmp_path):
    path = tmp_path / "queue.vdisk"
    disk = _new(path)
    queue = DurableQueue(disk.checkpoints)
    task = queue.enqueue({"value": 7}, idempotency_key="operation-1")
    claimed = queue.claim()
    original_save = queue._save
    fired = False

    def save(state):
        nonlocal fired
        original_save(state)
        if not fired and state["tasks"][task.id]["status"] == "succeeded":
            fired = True; raise Crash()

    queue._save = save
    with pytest.raises(Crash):
        queue.complete(claimed, {"answer": 7})
    disk.close()
    reopened = DataDisk(path).mount()
    queue2 = DurableQueue(reopened.checkpoints)
    result = queue2.enqueue({"value": 7}, idempotency_key="operation-1")
    assert result.id == task.id
    assert result.status == "succeeded"
    assert result.result == {"answer": 7}
    assert queue2.list("succeeded")[0].id == task.id
    reopened.close()
