"""Issue #1 B1: queued operations must survive a process restart."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from pyvdisk.execution import ExecutionContext, ExecutionService
from pyvdisk.infrastructure import CheckpointStore, DurableQueue
from pyvdisk.infrastructure.operations import (
    OperationError,
    OperationNotFound,
    OperationRegistry,
    RegisteredCallable,
    UnserializableOperation,
    describe_operation,
    register_callable,
)


def _add_numbers(a, b):
    return a + b


def _echo_payload(value):
    return value


class CrossProcessQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ops_dir = self.root / "ops"
        self.ops_dir.mkdir()

    def _build_registry(self, store=None, host_dir=None):
        if host_dir is None:
            host_dir = self.ops_dir
        return OperationRegistry(store=store, host_dir=host_dir)

    def test_registered_callable_survives_process_restart(self):
        register_callable("tests.test_cross_process_queue:_add_numbers", _add_numbers)
        registry = self._build_registry()
        payload = describe_operation(_add_numbers)
        payload["payload"]["args"] = [2, 3]
        payload["payload"]["kwargs"] = {}
        registry.save("op-callable-1", payload["kind"], payload["payload"])
        self.assertTrue(registry.has("op-callable-1"))
        fresh = self._build_registry()
        recovered = fresh.recover("op-callable-1")
        self.assertIsInstance(recovered, RegisteredCallable)
        self.assertEqual(recovered(), 5)

    def test_vscript_source_persists_and_recompiles(self):
        registry = self._build_registry()
        source = "x = 1 + 2; y = x * 10"
        record = describe_operation(source)
        registry.save("op-vscript-1", record["kind"], record["payload"])
        fresh = self._build_registry()
        recovered = fresh.recover("op-vscript-1")
        self.assertEqual(recovered, source)

    def test_payload_kind_round_trip(self):
        registry = self._build_registry()
        payload = {"k": "v", "n": 1, "nested": [1, 2, 3]}
        record = describe_operation(payload)
        registry.save("op-payload-1", record["kind"], record["payload"])
        self.assertEqual(registry.recover("op-payload-1"), payload)

    def test_unregistered_callable_raises_clear_error(self):
        registry = self._build_registry()
        registry.save("op-bad", "callable", {"name": "tests.test_cross_process_queue:does_not_exist", "args": [], "kwargs": {}})
        with self.assertRaises(OperationError) as cm:
            registry.recover("op-bad")
        self.assertIn("does_not_exist", str(cm.exception))

    def test_lambda_is_unserializable(self):
        with self.assertRaises(UnserializableOperation):
            describe_operation(lambda x: x + 1)

    def test_unknown_op_id_raises_not_found(self):
        registry = self._build_registry()
        with self.assertRaises(OperationNotFound):
            registry.recover("missing")

    def test_checkpoint_store_backend_isolated(self):
        a = CheckpointStore.from_host(self.root / "a")
        b = CheckpointStore.from_host(self.root / "b")
        ra = OperationRegistry(store=a, host_dir=None)
        rb = OperationRegistry(store=b, host_dir=None)
        record = describe_operation({"k": 1})
        ra.save("op-x", record["kind"], record["payload"])
        self.assertTrue(ra.has("op-x"))
        self.assertFalse(rb.has("op-x"))

    def test_execution_service_uses_persisted_callable(self):
        register_callable("tests.test_cross_process_queue:_add_numbers", _add_numbers)
        queue = DurableQueue(CheckpointStore.from_host(self.root / "queue"))
        service = ExecutionService(queue=queue, operations=OperationRegistry(store=queue.store))
        ctx = ExecutionContext(metadata={"args": (10, 20)})
        ctx.metadata["operation_id"] = "op-exec-1"
        service.enqueue_operation(_add_numbers, ctx)
        fresh_service = ExecutionService(queue=DurableQueue(CheckpointStore.from_host(self.root / "queue")),
                                         operations=OperationRegistry(store=queue.store))
        handle = fresh_service.run_next()
        self.assertIsNotNone(handle)
        self.assertEqual(handle.status, "succeeded")
        self.assertEqual(handle.result, 30)

    def test_execution_service_uses_persisted_vscript(self):
        queue = DurableQueue(CheckpointStore.from_host(self.root / "queue"))
        service = ExecutionService(queue=queue, operations=OperationRegistry(store=queue.store))
        ctx = ExecutionContext(metadata={"args": {}})
        ctx.metadata["operation_id"] = "op-exec-vs"
        service.enqueue_operation("print(7 * 6);", ctx)
        fresh_service = ExecutionService(queue=DurableQueue(CheckpointStore.from_host(self.root / "queue")),
                                         operations=OperationRegistry(store=queue.store))
        handle = fresh_service.run_next()
        self.assertIsNotNone(handle)
        self.assertEqual(handle.status, "succeeded")

    def test_lambda_falls_back_to_in_process_only(self):
        queue = DurableQueue(CheckpointStore.from_host(self.root / "queue"))
        service = ExecutionService(queue=queue, operations=OperationRegistry(store=queue.store))
        ctx = ExecutionContext(metadata={"args": (3,)})
        ctx.metadata["operation_id"] = "op-lambda"
        service.enqueue_operation(lambda: 6, ctx)
        self.assertFalse(service.operations.has("op-lambda"))
        handle = service.run_next()
        self.assertEqual(handle.status, "succeeded")
        self.assertEqual(handle.result, 6)


if __name__ == "__main__":
    unittest.main()
