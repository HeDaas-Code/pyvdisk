import unittest
from pyvdisk import ExecutionService, ExecutionContext

class ExecutionServiceTests(unittest.TestCase):
    def test_sync_callable_submit_and_run(self):
        service = ExecutionService()
        context = ExecutionContext(run_id="sync-1")
        handle = service.submit(lambda ctx: ctx.run_id, context)
        self.assertEqual(handle.status, "succeeded")
        self.assertEqual(handle.wait(), "sync-1")
        self.assertEqual(service.run(lambda: 42), 42)

    def test_vscript_receives_context_args(self):
        service = ExecutionService()
        context = ExecutionContext(metadata={"args": {"value": 7}})
        source = 'language "1.0"; let answer = arg("value") + 1; answer;'
        self.assertEqual(service.run(source, context), 8)

    def test_failure_terminal_state(self):
        handle = ExecutionService().submit(lambda: (_ for _ in ()).throw(ValueError("bad")))
        self.assertEqual(handle.status, "failed")
        with self.assertRaises(ValueError): handle.wait()
        self.assertFalse(handle.cancel())

if __name__ == "__main__": unittest.main()
