import json

from pyvdisk import DataDisk
from pyvdisk.cli import main


def test_status_is_read_only_and_reports_data_disk(tmp_path, capsys):
    path = tmp_path / "agent.vdisk"
    disk = DataDisk.create(str(path), 16 * 1024 * 1024)
    disk.close()

    assert main(["status", str(path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["type"] == "pyvdisk-data"
    assert payload["mounted"] is True
    assert set(payload["namespaces"]) >= {"fs", "vectors", "logs", "checkpoints", "wal"}
    assert payload["runs"] == {
        "cancelled": 0, "failed": 0, "pending": 0, "running": 0, "succeeded": 0
    }


def test_status_rejects_plain_vfs_image(tmp_path):
    from pyvdisk.vfs import VFS
    path = tmp_path / "plain.vdisk"
    VFS.create(path, 16 * 1024 * 1024)
    try:
        main(["status", str(path)])
    except Exception as exc:
        assert "data container" in str(exc)
    else:
        raise AssertionError("status unexpectedly accepted a plain VFS image")
