import threading
import unittest

from pyvdisk.contracts import (
    Capability, CapabilityGrant, Durability, DurabilityMode,
    Event, ExecutionContext, RunHandle,
)


class ContractsTest(unittest.TestCase):
    def test_capabilities_and_durability(self):
        grant = CapabilityGrant("job", frozenset({Capability.READ.value}), "/data")
        self.assertTrue(grant.allows("read", "/data"))
        self.assertFalse(grant.allows("write", "/data"))
        with self.assertRaises(PermissionError):
            grant.require("write")
        with self.assertRaises(ValueError):
            Durability(DurabilityMode.REPLICATED)

    def test_context_and_event_defaults(self):
        context = ExecutionContext(capabilities=(CapabilityGrant("job", frozenset({"write"})),))
        context.require("write")
        self.assertFalse(context.expired())
        self.assertEqual(Event("runs", {"ok": True}).stream, "runs")

    def test_run_handle_wait_and_failure(self):
        handle = RunHandle("run-1")
        thread = threading.Thread(target=lambda: handle.complete(42))
        thread.start()
        self.assertEqual(handle.wait(1), 42)
        thread.join()
        self.assertEqual(handle.status, "succeeded")
        failed = RunHandle("run-2")
        failed.fail(RuntimeError("boom"))
        with self.assertRaisesRegex(RuntimeError, "boom"):
            failed.wait()


if __name__ == "__main__":
    unittest.main()
