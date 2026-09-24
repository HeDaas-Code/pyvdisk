"""Issue #1 B2 + B7: one WAL implementation, and a log that can be truncated.

B2: the log used to grow forever and every mount replayed the whole history. A
checkpoint settles every recorded transaction (committed work is already published,
unfinished work is compensated) and then drops the log.
B7: DataDisk and VScript used two WAL implementations whose readers disagreed about
which record kinds exist, and VScript's ``recover`` had no caller outside tests.
"""
from __future__ import annotations

import argparse
import io

import pytest

from pyvdisk import DataDisk
from pyvdisk.infrastructure import wal as infra_wal
from pyvdisk.vscript import Compiler, Runtime
from pyvdisk.vscript.cli import command as vscript_command
from pyvdisk.vscript.mounts import MountRegistry
from pyvdisk.vscript.policy import Capability
from pyvdisk.vscript.runtime import recover_wal
from pyvdisk.vscript.stdlib import Handle
from pyvdisk.vscript.wal import WriteAheadLog


class Crash(BaseException):
    """Process-loss simulation: bypasses transaction exception cleanup."""


def _kill(disk):
    """Process death: release the image without running DataDisk shutdown."""
    disk.vfs.close()


def _crash_before_commit_record(disk):
    original = disk._append_metadata_wal
    fired = False

    def append(record):
        nonlocal fired
        original(record)
        if not fired and record.get("kind") == "apply":
            fired = True
            raise Crash()

    disk._append_metadata_wal = append


def _new(path):
    return DataDisk.create(path, 32 * 1024 * 1024).mount()


# --------------------------------------------------------------------------- B7
def test_vscript_and_datadisk_share_one_wal_implementation():
    from pyvdisk.vscript import wal as vscript_wal

    assert vscript_wal.WriteAheadLog is infra_wal.WriteAheadLog
    # One vocabulary: the kinds VScript's old reader rejected are now valid for both.
    assert {"intent", "prepare", "apply", "abort", "undo", "compensated"} <= infra_wal.RECORD_KINDS


def test_host_and_vfs_logs_share_the_record_codec(tmp_path):
    host = WriteAheadLog(tmp_path / "host.wal")
    disk = _new(tmp_path / "vfs.vdisk")
    try:
        embedded = WriteAheadLog(disk.vfs)
        for log in (host, embedded):
            txid = log.begin("tx")
            log.intent(txid, {"participant": "P", "count": 1})
            log.prepare(txid, {"participant": "P"})
            log.apply(txid)
            log.append(txid, {"key": "k", "after": "v"})
            log.commit(txid)
        assert [r["kind"] for r in host.records()] == [r["kind"] for r in embedded.records()]
        assert host.recover()[0][0][0] == "tx" and embedded.recover()[0][0][0] == "tx"
    finally:
        disk.close()


def test_recover_wal_rolls_back_a_pending_vscript_transaction(tmp_path):
    disk = _new(tmp_path / "pending.vdisk")
    wal = WriteAheadLog(tmp_path / "pending.wal")
    try:
        disk.fs.write_file("/notes.txt", b"hello")
        txid = wal.begin()
        wal.append(txid, {"kind": "write", "mount": "data", "path": "/notes.txt", "old": None, "new": "hello"})
        # No commit record: the process that wrote this died mid-transaction.

        report = recover_wal(wal, {"data": disk.fs})
        assert report["pending"] == [txid] and report["rolled_back"] == 1
        assert disk.fs.exists("/notes.txt") is False
        assert wal.size() == 0  # settled, so the log can go
    finally:
        disk.close()


def test_recover_wal_leaves_a_committed_vscript_transaction_alone(tmp_path):
    disk = _new(tmp_path / "committed.vdisk")
    wal = WriteAheadLog(tmp_path / "committed.wal")
    try:
        txid = wal.begin()
        wal.append(txid, {"kind": "write", "mount": "data", "path": "/out.txt", "old": None, "new": "written"})
        wal.commit(txid)
        # The write lands before the commit record, so recovery has nothing to redo:
        # replaying it is unnecessary for a write and would duplicate an append.
        disk.fs.write_file("/out.txt", b"written")

        report = recover_wal(wal, {"data": disk.fs})
        assert report["committed"] == [txid] and report["pending"] == [] and report["rolled_back"] == 0
        assert disk.fs.read_file("/out.txt") == b"written"
        assert wal.size() == 0
    finally:
        disk.close()


def test_recover_wal_keeps_the_log_when_a_mount_is_missing(tmp_path):
    disk = _new(tmp_path / "unknown.vdisk")
    wal = WriteAheadLog(tmp_path / "unknown.wal")
    try:
        txid = wal.begin()
        wal.append(txid, {"kind": "write", "mount": "gone", "path": "/x.txt", "old": None, "new": "y"})
        # Guessing which store an operation belonged to would be worse than reporting it,
        # and aborting the transaction would silently keep the half-applied write.
        report = recover_wal(wal, {})
        assert report["unresolved"] and report["rolled_back"] == 0
        assert report["deferred"] == [txid] and report["pending"] == []
        assert wal.size() > 0
    finally:
        disk.close()


def test_vscript_rollback_is_recorded_so_it_does_not_stay_pending(tmp_path):
    disk = _new(tmp_path / "rollback.vdisk")
    wal = WriteAheadLog(tmp_path / "rollback.wal")
    try:
        handle = Handle(Capability("data", "fs", frozenset({"read", "write"}), disk.fs, "/"))
        program = Compiler().compile('language "1.0"; try { transaction { fs.write(data,"/x","new"); throw "boom"; } } catch(e) { }')
        Runtime(stdout=io.StringIO(), wal=wal).run(program.ast, bindings={"data": handle})

        kinds = [record["kind"] for record in wal.records()]
        assert "begin" in kinds and "abort" in kinds and "commit" not in kinds
        # A rolled-back transaction is settled, not an in-flight transaction forever.
        assert wal.recover() == ((), ())
        assert disk.fs.exists("/x") is False
    finally:
        disk.close()


def test_mount_registry_binds_the_recorded_mount_name(tmp_path):
    disk_path = tmp_path / "named.vdisk"
    DataDisk.create(disk_path, 16 * 1024 * 1024).close()
    with MountRegistry() as mounts:
        handle = mounts.open("data", str(disk_path), permissions={"read", "write"})
        # Operations record cap.name, so a later process can resolve them by the same
        # name it passes to --mount.
        assert handle.cap.name == "data" and handle.cap.kind == "fs"


def test_cli_wal_recovers_a_pending_transaction_from_a_previous_process(tmp_path, capsys):
    image = tmp_path / "data.vdisk"
    disk = DataDisk.create(image, 32 * 1024 * 1024).mount()
    disk.fs.write_file("/notes.txt", b"hello")
    disk.close()

    wal_path = tmp_path / "tx.wal"
    wal = WriteAheadLog(wal_path)
    txid = wal.begin()
    wal.append(txid, {"kind": "write", "mount": "data", "path": "/notes.txt", "old": None, "new": "hello"})

    script = tmp_path / "noop.vds"
    script.write_text('language "1.0";\nlet untouched = 1;\n')
    code = vscript_command(argparse.Namespace(
        action="run", script=str(script), arg=[], mount=[f"data:{image}:read,write"], wal=str(wal_path),
    ))
    assert code == 0

    captured = capsys.readouterr()
    assert "回滚 1 个未完成事务" in captured.err
    # The half-finished write is gone and the settled log no longer re-reports it.
    reopened = DataDisk(image).mount()
    try:
        assert reopened.fs.exists("/notes.txt") is False
    finally:
        reopened.close()
    assert WriteAheadLog(wal_path).size() == 0


# --------------------------------------------------------------------------- B2
def test_close_checkpoint_truncates_a_settled_log(tmp_path):
    path = tmp_path / "settled.vdisk"
    disk = _new(path)
    disk.fs.write_file("/keep.txt", b"original")
    with disk.transaction() as tx:
        tx.set("answer", 42)
        disk.fs.write_file("/keep.txt", b"changed")
    assert disk.wal_stats()["bytes"] > 0

    disk.close()
    reopened = DataDisk(path).mount()
    try:
        assert reopened.wal_stats()["bytes"] == 0
        assert reopened.wal_stats()["checkpoint"]["truncated_records"] > 0
        # Committed work is published, so it needs no redo after a checkpoint.
        assert reopened.get_metadata("answer") == 42
        assert reopened.fs.read_file("/keep.txt") == b"changed"
        assert reopened.recovery_report() == {"compensated": [], "committed": [], "aborted": [], "participants": []}
    finally:
        reopened.close()


def test_log_stays_bounded_across_many_transactions(tmp_path):
    path = tmp_path / "bounded.vdisk"
    disk = _new(path)
    disk.WAL_CHECKPOINT_BYTES = 4096
    for index in range(60):
        with disk.transaction() as tx:
            tx.set(f"k{index}", index)
    # Without truncation this would be the whole history; the log is one checkpoint old.
    assert disk.wal_stats()["bytes"] < 4096 + 4096
    assert disk.get_metadata("k59") == 59
    disk.close()

    reopened = DataDisk(path).mount()
    try:
        assert reopened.get_metadata("k0") == 0 and reopened.get_metadata("k59") == 59
    finally:
        reopened.close()


def test_open_transaction_pins_the_log_against_truncation(tmp_path):
    path = tmp_path / "pinned.vdisk"
    disk = _new(path)
    with disk.transaction() as tx:
        tx.set("answer", 42)
        disk.fs.write_file("/x.txt", b"x")
        # Dropping the log mid-transaction would lose the only record of the undo.
        assert disk.checkpoint_wal() is None
    assert disk.wal_stats()["bytes"] > 0
    assert disk.checkpoint_wal()["truncated_records"] > 0
    assert disk.wal_stats()["bytes"] == 0
    disk.close()


def test_truncation_still_compensates_a_later_crash(tmp_path):
    path = tmp_path / "after.vdisk"
    disk = _new(path)
    disk.fs.write_file("/keep.txt", b"original")
    with disk.transaction() as tx:
        tx.set("committed", True)
    disk.checkpoint_wal()
    assert disk.wal_stats()["bytes"] == 0

    _crash_before_commit_record(disk)
    with pytest.raises(Crash):
        with disk.transaction() as tx:
            tx.set("answer", 42)
            disk.fs.write_file("/keep.txt", b"crash")
    _kill(disk)

    reopened = DataDisk(path).mount()
    try:
        assert reopened.get_metadata("answer") is None
        assert reopened.get_metadata("committed") is True
        assert reopened.fs.read_file("/keep.txt") == b"original"
    finally:
        reopened.close()
