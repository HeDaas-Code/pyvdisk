from pyvdisk import DataDisk
from pyvdisk.infrastructure.wal import WriteAheadLog

def test_abort_recovery_is_ignored_and_repeatable(tmp_path):
    disk = DataDisk.create(tmp_path / "d.vdisk", 8 * 1024 * 1024).mount()
    try:
        wal = WriteAheadLog(disk.vfs)
        tx = wal.begin("aborted")
        wal.append(tx, {"x": 1})
        wal.abort(tx)
        assert wal.recover() == ((), ())
        assert wal.recover() == ((), ())
    finally:
        disk.close()

def test_wal_reader_does_not_stop_at_transaction_record_kinds(tmp_path):
    """The shared log carries metadata *and* compensation records; readers must read all of it."""
    disk = DataDisk.create(tmp_path / "kinds.vdisk", 8 * 1024 * 1024).mount()
    try:
        with disk.transaction() as tx:
            tx.set("answer", 42)
            disk.fs.write_file("/x.txt", b"x")
        kinds = [record["kind"] for record in disk.wal.records()]
        assert {"begin", "undo", "operation", "apply", "commit"} <= set(kinds)
        # Every record is readable, so the log is not truncated at the first undo record.
        assert kinds[-1] == "commit"
    finally:
        disk.close()
