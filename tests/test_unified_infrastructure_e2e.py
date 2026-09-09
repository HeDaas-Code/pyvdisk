import math
import tempfile
import unittest
from pathlib import Path

from pyvdisk import (
    Capability, CapabilityGrant, DataDisk, ExecutionContext, ExecutionService,
    LogEvent,
)
from pyvdisk.infrastructure import (
    CheckpointStore, DataDiskError, DurableQueue, TransactionParticipant,
    WriteAheadLog, RunStateStore, scoped,
)
from pyvdisk.vscript.audit import DataDiskAuditSink


class UnifiedInfrastructureEndToEndTests(unittest.TestCase):
    def make_disk(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "unified.vdisk"
        disk = DataDisk.create(path, 32 * 1024 * 1024)
        self.addCleanup(lambda: (disk.close(), td.cleanup()))
        return disk, path

    def test_one_file_namespaces_and_close_remount(self):
        disk, path = self.make_disk()
        with disk.mount():
            self.assertTrue(disk.fs.exists("/.system/manifest.json"))
            disk.fs.write_file("/hello", b"world")
            disk.vector.create_collection("items", 2, max_elements=4)
            disk.vector.upsert("items", "a", [1, 0], {"kind": "x"})
            disk.log.create_stream("events")
            first = disk.log.append("events", LogEvent(1, "INFO", "test", "one"))
            second = disk.log.append("events", LogEvent(2, "INFO", "test", "two"))
            disk.checkpoints.mark_success("job", first.event_id)
            self.assertEqual(first.sequence, 0)
            self.assertEqual(second.sequence, 1)
            self.assertEqual(disk.vector.get("items", "a")["vector"], [1.0, 0.0])
        reopened = DataDisk(path).mount()
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.fs.read_file("/hello"), b"world")
        self.assertEqual(reopened.vector.count("items"), 1)
        self.assertEqual([e.sequence for e in reopened.log.query("events")], [0, 1])
        self.assertEqual(reopened.checkpoints.last_event("job"), first.event_id)

    def test_scoped_capability_and_finite_vector_validation(self):
        disk, _ = self.make_disk()
        disk.mount()
        context = ExecutionContext(capabilities=(
            CapabilityGrant("fs", frozenset({Capability.READ.value, Capability.WRITE.value}), "/public"),
            CapabilityGrant("vector", frozenset({Capability.READ.value, Capability.WRITE.value, Capability.ADMIN.value}), "/items"),
            CapabilityGrant("log", frozenset({"append", "read", "admin"}), "/events"),
            CapabilityGrant("checkpoint", frozenset({"read", "write"}), "/job"),
        ))
        view = scoped(disk, context)
        view.fs.makedirs("/public")
        view.fs.write_file("/public/a", b"a")
        with self.assertRaises(PermissionError): view.fs.write_file("/private/a", b"x")
        with self.assertRaises(PermissionError): view.fs.read_file("/.system/manifest.json")
        view.vector.create_collection("items", 2)
        with self.assertRaises(Exception): view.vector.upsert("items", "bad", [math.nan, 1])
        with self.assertRaises(PermissionError): view.vector.upsert("other", "x", [1, 2])

    def test_execution_runstate_queue_and_audit(self):
        disk, _ = self.make_disk(); disk.mount()
        audit = DataDiskAuditSink(disk, "audit")
        store = CheckpointStore(disk.vfs, "/.system/queue-checkpoint.json")
        queue = DurableQueue(store)
        service = ExecutionService(disk, queue=queue, audit_sink=audit)
        context = ExecutionContext(run_id="run-e2e")
        task = service.enqueue_operation(lambda ctx, d: (ctx.run_id, d.mounted), context)
        handle = service.run_next()
        self.assertEqual(handle.wait(), ("run-e2e", True))
        self.assertEqual(service.run_state.get("run-e2e").status, "succeeded")
        self.assertEqual(queue.get(task.id).status, "succeeded")

    def test_log_replay_ack_and_wal_lifecycle(self):
        disk, _ = self.make_disk(); disk.mount(); disk.log.create_stream("stream")
        events = disk.log.append_many("stream", [LogEvent(1, "INFO", "t", "a"), LogEvent(2, "INFO", "t", "b")])
        self.assertEqual([e.sequence for e in disk.log.replay("stream")], [0, 1])
        disk.log.ack("stream", "consumer", events[0].sequence)
        self.assertEqual([e.sequence for e in disk.log.replay("stream", "consumer")], [1])
        disk.log.ack("stream", "consumer", events[1].sequence)
        self.assertEqual(disk.log.replay("stream", "consumer"), [])
        wal = disk.wal; txid = wal.begin("tx"); wal.append(txid, {"x": 1}); wal.commit(txid)
        done, pending = wal.recover(); self.assertEqual(done[0][0], "tx"); self.assertFalse(pending)

    def test_transaction_participant_lifecycle_and_remount_recovery(self):
        disk, path = self.make_disk(); disk.mount()
        calls = []
        class Participant(TransactionParticipant):
            def prepare(self, txid, intents): calls.append("prepare")
            def commit(self, txid, intents): calls.append("commit")
            def abort(self, txid, intents): calls.append("abort")
        with disk.transaction() as tx:
            tx.set("answer", 42).enlist(Participant(), {"op": "set"})
        self.assertEqual(calls, ["prepare", "commit"])
        disk.close(); remounted = DataDisk(path).mount(); self.addCleanup(remounted.close)
        self.assertEqual(remounted.get_metadata("answer"), 42)


if __name__ == "__main__":
    unittest.main()
