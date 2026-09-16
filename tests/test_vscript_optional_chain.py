"""Issue #1 A4: optional chaining (?.) in VScript."""
from __future__ import annotations

import unittest

from pyvdisk.vscript import Compiler, Runtime
from pyvdisk.vscript.policy import Policy


def _run(src):
    program = Compiler().compile(src)
    rt = Runtime(policy=Policy())
    return rt.run(program.ast, source=src)


class OptionalChainTests(unittest.TestCase):
    def test_optional_member_on_none_returns_none(self):
        v = _run("let x = null; x?.name;")
        self.assertIsNone(v)

    def test_optional_member_on_value_returns_field(self):
        v = _run("let d = {\"a\": 1}; d?.a;")
        self.assertEqual(v, 1)

    def test_optional_member_missing_field_returns_none(self):
        v = _run("let d = {\"a\": 1}; d?.missing;")
        self.assertIsNone(v)

    def test_plain_member_on_none_still_errors(self):
        with self.assertRaises(Exception):
            _run("let x = null; x.name;")


if __name__ == "__main__":
    unittest.main()
