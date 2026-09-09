from pyvdisk.infrastructure import DataDisk

def test_transaction_repeated_commit_abort_are_safe(tmp_path):
    disk = DataDisk.create(tmp_path / "x.vdisk", 16 * 1024 * 1024).mount()
    try:
        tx = disk.transaction().set("x", 1)
        tx.commit(); tx.commit(); assert disk.get_metadata("x") == 1
        aborted = disk.transaction().set("y", 2)
        aborted.abort(); aborted.abort(); assert disk.get_metadata("y") is None
    finally:
        disk.close()
