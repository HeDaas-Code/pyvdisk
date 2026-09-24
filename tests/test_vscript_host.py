import argparse
import io
import os
import tempfile
import unittest
from pathlib import Path
from pyvdisk.vscript import Compiler, Runtime
from pyvdisk.vscript.cli import add_parser as add_vscript_parser
from pyvdisk.vscript.errors import CapabilityError
from pyvdisk.vscript.host import HostCapability
from pyvdisk.vscript.policy import Policy

class HostCapabilityTests(unittest.TestCase):
    def test_allowlist_and_policy(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"in").write_bytes(b"ok")
            p=HostCapability([root], [root]).proxy()
            self.assertEqual(p.read(root/"in"), b"ok")
            p.write(root/"out", b"new")
            self.assertEqual((root/"out").read_bytes(), b"new")
    def test_symlink_escape_and_special_files_rejected(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            root=Path(td); (root/"link").symlink_to(outside, target_is_directory=True)
            (Path(outside)/"secret").write_bytes(b"secret")
            p=HostCapability([root], [root]).proxy()
            with self.assertRaises(CapabilityError): p.read(root/"link"/"secret")
            with self.assertRaises(CapabilityError): p.write(root/"link"/"new", b"x")
            if hasattr(os, "mkfifo"):
                os.mkfifo(root/"pipe")
                with self.assertRaises(CapabilityError): p.read(root/"pipe")
    def test_read_and_write_roots_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); read=root/"read"; write=root/"write"; read.mkdir(); write.mkdir()
            p=HostCapability([read], [write]).proxy()
            (read/"x").write_bytes(b"x")
            self.assertEqual(p.read(read/"x"), b"x")
            with self.assertRaises(CapabilityError): p.write(read/"bad", b"x")
            with self.assertRaises(CapabilityError): p.read(write/"missing")

    def test_unauthorized_root_says_how_to_authorize(self):
        """C9: an empty root list is a policy that granted nothing, and must say so.

        The message used to blame the requested path ("宿主路径不在允许的根目录"),
        which hid the real cause: nothing in the CLI or REPL ever injected a root.
        """
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"f"; target.write_bytes(b"x")
            p=HostCapability().proxy()
            with self.assertRaises(CapabilityError) as caught: p.read(target)
            self.assertIn("--host-read-root", str(caught.exception))
            with self.assertRaises(CapabilityError) as caught: p.write(target, b"y")
            self.assertIn("--host-write-root", str(caught.exception))


def _run(source, policy=None, **kw):
    out = io.StringIO()
    program = Compiler().compile(source)
    runtime = Runtime(stdout=out, policy=policy, **kw)
    runtime.run(program.ast)
    return out.getvalue()


class HostModuleThroughRuntimeTests(unittest.TestCase):
    """C9: the bridge is only reachable if a policy actually names a root."""

    def test_host_module_is_unauthorized_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "f.txt"
            target.write_bytes(b"x")
            with self.assertRaises(CapabilityError) as caught:
                _run(f'language "1.0"; host.read("{target}");')
            self.assertIn("--host-read-root", str(caught.exception))

    def test_policy_roots_make_host_read_write_and_import_work(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "in.txt").write_bytes(b"hello-host")
            policy = Policy(host_read_roots=[str(root)], host_write_roots=[str(root)])
            _run(
                f'language "1.0";'
                f'let d = host.read("{root}/in.txt");'
                f'assert d.length == 10;'
                f'host.write("{root}/out.txt", d);'
                f'host.write("{root}/second.txt", "second");',
                policy=policy,
            )
            self.assertEqual((root / "out.txt").read_bytes(), b"hello-host")
            self.assertEqual((root / "second.txt").read_bytes(), b"second")

    def test_policy_roots_do_not_widen_to_unrelated_paths(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "secret.txt").write_bytes(b"secret")
            policy = Policy(host_read_roots=[td], host_write_roots=[td])
            with self.assertRaises(CapabilityError):
                _run(f'language "1.0"; host.read("{outside}/secret.txt");', policy=policy)


class HostCliTests(unittest.TestCase):
    def _parser(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command", required=True)
        add_vscript_parser(sub)
        return parser

    def test_cli_registers_host_root_switches(self):
        """The switches must exist on every action that builds a Runtime."""
        parser = self._parser()
        for action in ("run", "run-disk", "repl"):
            argv = ["vscript", action, "x.vds"] if action != "repl" else ["vscript", action]
            parsed = parser.parse_args(argv + ["--host-read-root", "/tmp", "--host-write-root", "/tmp"])
            self.assertEqual(parsed.host_read_root, ["/tmp"], action)
            self.assertEqual(parsed.host_write_root, ["/tmp"], action)

    def test_cli_run_grants_host_access(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "in.txt").write_bytes(b"payload")
            script = root / "s.vds"
            script.write_text(
                f'language "1.0"; let d = host.read("{root}/in.txt");'
                f'host.write("{root}/out.txt", d);',
                encoding="utf-8",
            )
            args = self._parser().parse_args([
                "vscript", "run", str(script),
                "--host-read-root", str(root), "--host-write-root", str(root),
            ])
            self.assertEqual(args.func(args), 0)
            self.assertEqual((root / "out.txt").read_bytes(), b"payload")

    def test_cli_run_without_roots_reports_capability_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "in.txt").write_bytes(b"payload")
            script = root / "s.vds"
            script.write_text(f'language "1.0"; host.read("{root}/in.txt");', encoding="utf-8")
            args = self._parser().parse_args(["vscript", "run", str(script)])
            self.assertEqual(args.func(args), 3)


if __name__ == "__main__": unittest.main()
