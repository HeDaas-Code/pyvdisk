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
