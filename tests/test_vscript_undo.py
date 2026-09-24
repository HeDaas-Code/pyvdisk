"""Issue #1 C8: every mutating fs operation is undoable, and bodies stay off-heap.

Two defects lived here. Only ``fs.write``/``fs.append`` recorded an undo, so a
rollback left ``remove``/``mkdir``/``move``/``link`` applied; and the undo held the
old file body in memory for the transaction's whole lifetime.

The tests come in pairs on purpose: an in-process rollback has live handles, while
a crash recovery has only the log, and both paths must reach the same state.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

import pytest

from pyvdisk import DataDisk
from pyvdisk.vscript import Compiler, Runtime
from pyvdisk.vscript.mounts import MountRegistry
from pyvdisk.vscript.runtime import TransactionContext, recover_wal
from pyvdisk.vscript.undo import (
    KINDS,
    SPILL_ROOT,
    SPILL_THRESHOLD,
    apply_undo,
    copy_tree,
    normalize,
)
from pyvdisk.vscript.wal import WriteAheadLog

PERMISSIONS = {"read", "write", "delete", "admin"}


class _Disk:
    """A mounted fs disk whose only shared state between "processes" is the log."""

    def __init__(self, tmp):
        self.image = Path(tmp) / "data.vdisk"
        DataDisk.create(str(self.image), 16 * 1024 * 1024).close()
        self.wal_path = Path(tmp) / "tx.wal"
        self.mounts = MountRegistry()
        self.handle = self.mounts.open("data", str(self.image), permissions=PERMISSIONS)

    @property
    def fs(self):
        return self.handle.cap.target

    def close(self):
        self.mounts.close()

    def rollback(self, body):
        """Run `body` inside a transaction that throws, and swallow the throw."""
        script = 'language "1.0"; try { transaction {\n' + body + '\n throw "abort"; } } catch(e) { }'
        Runtime(stdout=io.StringIO()).run(
            Compiler().compile(script).ast, bindings={"data": self.handle}
        )

    def crash(self, body):
        """Run `body` under a transaction that is never settled, then drop everything.

        This is the process-death simulation: the mutation has happened, the log has
        the entry, and nothing in memory will ever undo it. Handles are closed so the
        recovery below has to work from the log and the store alone.
        """
        wal = WriteAheadLog(self.wal_path)
        runtime = Runtime(stdout=io.StringIO(), wal=wal, mount_registry=self.mounts)
        tx = TransactionContext(runtime)
        runtime._transactions.append(tx)
        try:
            Runtime.run(runtime, Compiler().compile('language "1.0";\n' + body).ast,
                        bindings={"data": self.handle})
        finally:
            runtime._transactions.pop()
        self.close()

    def reopen(self):
        """A fresh process: reopen the image, without touching the log."""
        self.mounts.close()
        self.mounts = MountRegistry()
        self.handle = self.mounts.open("data", str(self.image), permissions=PERMISSIONS)
        return self.fs

    def recover(self):
        """Settle whatever transaction the log still holds."""
        self.reopen()
        return recover_wal(WriteAheadLog(self.wal_path), {"data": self.fs})


@pytest.fixture
def disk(tmp_path):
    d = _Disk(tmp_path)
    yield d
    d.close()


# ------------------------------------------------------------------ in-process rollback
def test_mkdir_and_makedirs_are_removed_by_rollback(disk):
    disk.rollback('fs.mkdir(data,"/one"); fs.mkdir(data,"/deep/two",true);')
    assert disk.fs.exists("/one") is False
    assert disk.fs.exists("/deep") is False


def test_removed_file_is_restored_by_rollback(disk):
    disk.fs.write_file("/keep.txt", b"original")
    disk.rollback('fs.remove(data,"/keep.txt");')
    assert disk.fs.read_file("/keep.txt") == b"original"


def test_removed_tree_is_restored_by_rollback(disk):
    disk.fs.makedirs("/d/sub")
    disk.fs.write_file("/d/a.txt", b"A")
    disk.fs.write_file("/d/sub/b.txt", b"B")
    disk.fs.symlink("a.txt", "/d/link")
    disk.rollback('fs.remove(data,"/d",true);')
    assert disk.fs.read_file("/d/a.txt") == b"A"
    assert disk.fs.read_file("/d/sub/b.txt") == b"B"
    assert disk.fs.isdir("/d/sub")
    assert disk.fs.readlink("/d/link") == "a.txt"


def test_move_is_reverted_by_rollback(disk):
    disk.fs.write_file("/src.txt", b"src")
    disk.rollback('fs.move(data,"/src.txt","/dst.txt");')
    assert disk.fs.read_file("/src.txt") == b"src"
    assert disk.fs.exists("/dst.txt") is False


def test_move_onto_an_existing_path_restores_it(disk):
    disk.fs.write_file("/src.txt", b"src")
    disk.fs.write_file("/dst.txt", b"dst-before")
    disk.rollback('fs.move(data,"/src.txt","/dst.txt");')
    assert disk.fs.read_file("/src.txt") == b"src"
    assert disk.fs.read_file("/dst.txt") == b"dst-before"


def test_link_and_symlink_are_removed_by_rollback(disk):
    disk.fs.write_file("/a.txt", b"A")
    disk.rollback('fs.link(data,"/a.txt","/hard"); fs.symlink(data,"a.txt","/soft");')
    assert disk.fs.exists("/hard") is False
    assert disk.fs.exists("/soft") is False
    assert disk.fs.read_file("/a.txt") == b"A"


def test_copy_destination_is_undone_by_rollback(disk):
    disk.fs.write_file("/from.txt", b"payload")
    disk.fs.write_file("/onto.txt", b"before")
    disk.rollback(
        'fs.copy(data,"/from.txt",data,"/fresh.txt");'
        'fs.copy(data,"/from.txt",data,"/onto.txt",true);'
    )
    assert disk.fs.exists("/fresh.txt") is False
    assert disk.fs.read_file("/onto.txt") == b"before"


def test_truncate_is_reverted_by_rollback(disk):
    disk.fs.write_file("/t.txt", b"0123456789")
    disk.rollback('fs.truncate(data,"/t.txt",3);')
    assert disk.fs.read_file("/t.txt") == b"0123456789"


def test_metadata_is_restored_by_rollback(disk):
    disk.fs.write_file("/m.txt", b"x")
    before = disk.fs.stat("/m.txt")
    disk.rollback(
        'fs.chmod(data,"/m.txt",0o600);'
        'fs.utime(data,"/m.txt",12345,12345);'
    )
    after = disk.fs.stat("/m.txt")
    assert after.mode == before.mode
    assert after.mtime == before.mtime


# ------------------------------------------------------------------ crash recovery
def test_crash_after_remove_restores_from_the_log_alone(disk):
    disk.fs.write_file("/keep.txt", b"original")
    disk.crash('fs.remove(data,"/keep.txt");')
    assert disk.reopen().exists("/keep.txt") is False

    report = disk.recover()
    assert report["rolled_back"] == 1 and report["deferred"] == []
    assert disk.fs.read_file("/keep.txt") == b"original"


def test_crash_after_recursive_remove_restores_the_tree(disk):
    disk.fs.makedirs("/d/sub")
    disk.fs.write_file("/d/a.txt", b"A")
    disk.fs.write_file("/d/sub/b.txt", b"B")
    disk.crash('fs.remove(data,"/d",true);')
    assert disk.reopen().exists("/d") is False

    disk.recover()
    assert disk.fs.read_file("/d/a.txt") == b"A"
    assert disk.fs.read_file("/d/sub/b.txt") == b"B"


def test_crash_after_move_mkdir_and_chmod_is_settled(disk):
    disk.fs.write_file("/src.txt", b"src")
    disk.fs.write_file("/locked.txt", b"x")
    before = disk.fs.stat("/locked.txt").mode
    disk.crash(
        'fs.move(data,"/src.txt","/dst.txt");'
        'fs.mkdir(data,"/created");'
        'fs.chmod(data,"/locked.txt",0o600);'
    )
    assert disk.reopen().exists("/dst.txt") and disk.fs.exists("/created")

    report = disk.recover()
    assert report["rolled_back"] == 3 and report["deferred"] == []
    assert disk.fs.read_file("/src.txt") == b"src"
    assert disk.fs.exists("/dst.txt") is False
    assert disk.fs.exists("/created") is False
    assert disk.fs.stat("/locked.txt").mode == before


def test_committed_transaction_is_not_compensated(disk):
    script = (
        'language "1.0"; transaction { fs.write(data,"/keep.txt","kept");'
        ' fs.remove(data,"/gone.txt",true); }'
    )
    disk.fs.write_file("/gone.txt", b"content")
    wal = WriteAheadLog(disk.wal_path)
    Runtime(stdout=io.StringIO(), wal=wal, mount_registry=disk.mounts).run(
        Compiler().compile(script).ast, bindings={"data": disk.handle}
    )
    disk.close()

    report = disk.recover()
    assert report["rolled_back"] == 0
    assert disk.fs.read_file("/keep.txt") == b"kept"
    assert disk.fs.exists("/gone.txt") is False


# ------------------------------------------------------------------ bodies stay off-heap
def _journaled_entries(disk, body):
    """Return the entries one transaction journals, without settling it."""
    wal = WriteAheadLog(disk.wal_path)
    runtime = Runtime(stdout=io.StringIO(), wal=wal, mount_registry=disk.mounts)
    tx = TransactionContext(runtime)
    runtime._transactions.append(tx)
    try:
        Runtime.run(runtime, Compiler().compile('language "1.0";\n' + body).ast,
                    bindings={"data": disk.handle})
    finally:
        runtime._transactions.pop()
    return runtime, tx, wal


def test_a_large_body_is_spilled_instead_of_held_in_memory(disk):
    payload = bytes(range(256)) * (SPILL_THRESHOLD // 128)  # comfortably above the threshold
    disk.fs.write_file("/big.bin", payload)

    runtime, tx, wal = _journaled_entries(disk, 'fs.write(data,"/big.bin","tiny");')
    entry, = tx.operations
    assert entry["undo"] == "write"
    assert entry["spill"].startswith(SPILL_ROOT)
    assert "data" not in entry
    # Nothing in the entry -- or in the log -- carries the old body any more.
    assert max(len(v) for v in entry.values() if isinstance(v, (str, bytes))) < 256
    record = [r for r in wal.records() if r["kind"] == "operation"][-1]
    assert len(json.dumps(record)) < 4096
    assert disk.fs.read_file(entry["spill"]) == payload

    tx.rollback()
    assert disk.fs.read_file("/big.bin") == payload
    assert disk.fs.exists(entry["spill"]) is False


def test_a_small_body_stays_inline(disk):
    disk.fs.write_file("/small.txt", b"small")
    runtime, tx, wal = _journaled_entries(disk, 'fs.write(data,"/small.txt","new");')
    entry, = tx.operations
    assert entry["data"] == "small" and "spill" not in entry
    assert disk.fs.exists(SPILL_ROOT) is False
    tx.rollback()
    assert disk.fs.read_file("/small.txt") == b"small"


def test_spill_is_discarded_on_commit(disk):
    payload = b"x" * (SPILL_THRESHOLD + 1)
    disk.fs.write_file("/big.bin", payload)
    runtime, tx, wal = _journaled_entries(disk, 'fs.write(data,"/big.bin","tiny");')
    entry, = tx.operations
    assert disk.fs.exists(entry["spill"])
    tx.commit()
    assert disk.fs.exists(entry["spill"]) is False
    assert disk.fs.read_file("/big.bin") == b"tiny"


# ------------------------------------------------------------------ vocabulary
def test_journaled_verbs_are_all_understood():
    """Every verb the stdlib records has to be one the interpreter knows."""
    source = (Path(__file__).resolve().parents[1] / "pyvdisk" / "vscript" / "stdlib.py").read_text(encoding="utf-8")
    verbs = set()
    for line in source.splitlines():
        if "runtime.journal(" in line:
            verbs.update(re.findall(r'"([a-z_]+)"', line))
    assert verbs, "the stdlib no longer journals anything"
    assert verbs <= KINDS, f"journaled but unknown: {sorted(verbs - KINDS)}"


def test_every_verb_in_the_vocabulary_is_implemented(disk):
    """No verb may fall through to the unknown-entry return value.

    Each verb gets its own path so one undo cannot destroy the next one's setup.
    """
    fs = disk.fs
    fs.makedirs("/tree/sub")
    fs.write_file("/tree/sub/f", b"F")
    fs.makedirs("/spill")
    copy_tree(fs, "/tree", "/spill/copy")
    fs.write_file("/gone", b"gone")
    fs.symlink("gone", "/soft")
    fs.makedirs("/empty")
    fs.write_file("/moved", b"m")
    fs.write_file("/meta", b"x")
    fs.write_file("/trunc", b"01234")
    entries = [
        {"undo": "write", "path": "/gone", "data": None},
        {"undo": "remove", "path": "/soft"},
        {"undo": "mkdir", "path": "/empty"},
        {"undo": "rename", "path": "/moved", "to": "/origin"},
        {"undo": "meta", "path": "/meta", "mode": 0o644},
        {"undo": "truncate", "path": "/trunc", "size": 2},
        {"undo": "restore_tree", "path": "/restored", "spill": "/spill/copy"},
        {"undo": "symlink", "path": "/new-soft", "link_target": "gone"},
    ]
    assert {e["undo"] for e in entries} == KINDS
    for entry in entries:
        assert apply_undo(fs, entry) is True, entry


def test_entries_written_by_an_earlier_version_are_still_readable(disk):
    """A log from before this vocabulary carried ``kind``/``old``."""
    disk.fs.write_file("/legacy.txt", b"legacy")
    legacy = {"kind": "write", "mount": "data", "path": "/legacy.txt", "old": None, "new": "legacy"}
    assert normalize(legacy) == {"undo": "write", "path": "/legacy.txt", "data": None}
    assert apply_undo(disk.fs, normalize(legacy)) is True
    assert disk.fs.exists("/legacy.txt") is False


def test_unknown_entries_are_reported_not_guessed(disk):
    assert apply_undo(disk.fs, {"undo": "drop-everything"}) is False


def test_a_removal_that_would_swallow_the_snapshot_is_refused(disk):
    """Better a clear refusal than an undo that cannot be replayed."""
    disk.fs.makedirs("/d/sub")
    disk.fs.write_file("/d/sub/f", b"F")
    with pytest.raises(Exception) as caught:
        disk.rollback('fs.remove(data,"/",true);')
    assert "撤销快照" in str(caught.value)
    assert disk.fs.read_file("/d/sub/f") == b"F"


def test_recovery_drops_spills_orphaned_by_a_committed_transaction(disk):
    """A process that died between commit and cleanup leaves no bodies behind."""
    disk.fs.write_file("/x", b"x")
    spill = f"{SPILL_ROOT}/abcdef012345-0001"
    disk.fs.makedirs(SPILL_ROOT)
    disk.fs.write_file(spill, b"orphaned old body")

    wal = WriteAheadLog(disk.wal_path)
    txid = wal.begin()
    wal.append(txid, {"undo": "write", "mount": "data", "path": "/x", "spill": spill})
    wal.commit(txid)
    disk.close()

    report = disk.recover()
    assert report["rolled_back"] == 0  # committed work is never compensated
    assert disk.fs.read_file("/x") == b"x"
    assert disk.fs.exists(SPILL_ROOT) is False
