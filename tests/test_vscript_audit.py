import unittest
from pyvdisk.vscript import Compiler, Runtime, script_hash, policy_hash

class AuditTests(unittest.TestCase):
    def test_runtime_emits_audit_record(self):
        records = []
        source = "language \"1.0\"; let value=1;"
        program = Compiler().compile(source)
        Runtime(audit_callback=records.append).run(program.ast, source=program.source, run_id="run-1")
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.run_id, "run-1")
        self.assertEqual(record.status, "success")
        self.assertEqual(record.script_hash, script_hash(source))
        self.assertEqual(record.policy_hash, policy_hash(Runtime().policy))
        self.assertGreater(record.metrics["steps"], 0)
        self.assertIn("duration_ms", record.metrics)

if __name__ == "__main__":
    unittest.main()
