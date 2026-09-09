"""Runtime verification contracts; real desktop tests are explicitly opt-in."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "verify_runtime.py"
spec = importlib.util.spec_from_file_location("verify_runtime", MODULE)
runtime_tool = importlib.util.module_from_spec(spec) if MODULE.exists() else None
if runtime_tool is not None:
    spec.loader.exec_module(runtime_tool)


def pe_file(path, machine=0x8664):
    data = bytearray(256)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3c, 128)
    data[128:132] = b"PE\0\0"
    struct.pack_into("<H", data, 132, machine)
    path.write_bytes(data)


class RuntimeUnitTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(runtime_tool, "runtime verifier has not been implemented")
        self.temp = tempfile.TemporaryDirectory(prefix="vcxsrv unit ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runtime = self.root / "runtime with spaces"
        self.runtime.mkdir()
        self.output = self.root / "evidence"
        self.system32 = self.root / "System32"
        self.system32.mkdir()
        self.dumpbin = self.root / "tools with spaces" / "dumpbin.exe"
        self.dumpbin.parent.mkdir()
        self.dumpbin.touch()
        for name in ("vcxsrv.exe", "xauth.exe", "xwininfo.exe"):
            pe_file(self.runtime / name)
        self.children = []
        self.commands = []
        self.mode = "success"
        self.dependencies = "  Image has the following dependencies:\n\n  Summary\n"
        self.dumpbin_exit = 0
        self.auth_paths = []
        self.cookie = None
        self.real_popen = subprocess.Popen
        self.addCleanup(self.cleanup_children)
        self.addCleanup(patch.stopall)
        patch.object(runtime_tool, "require_host", return_value=self.system32).start()
        patch.object(runtime_tool.subprocess, "Popen", side_effect=self.launch).start()

    def cleanup_children(self):
        for child in self.children:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)

    def launch(self, args, **kwargs):
        # Replace only external executable behavior; process handles, timeouts,
        # logs, sockets, report writing and cleanup execute for real.
        self.commands.append((list(args), dict(kwargs["env"])))
        executable = Path(args[0]).name.lower()
        if executable == "dumpbin.exe":
            script = f"import sys; print({self.dependencies!r}); sys.exit({self.dumpbin_exit})"
        elif executable == "xauth.exe":
            auth = Path(args[args.index("-f") + 1])
            self.auth_paths.append(auth)
            self.cookie = args[-1]
            script = f"from pathlib import Path; Path({str(auth)!r}).write_text('temporary authority')"
            if self.mode in ("auth_failure", "auth_timeout"):
                script += f"; import sys; print({self.cookie!r}, flush=True); print({self.cookie!r}, file=sys.stderr, flush=True)"
                script += "; raise SystemExit(5)" if self.mode == "auth_failure" else "; import time; time.sleep(60)"
        elif executable == "vcxsrv.exe" and "-version" in args:
            script = "print('VcXsrv test version')"
        elif executable == "vcxsrv.exe":
            script = "import time; time.sleep(60)" if self.mode != "server_exit" else "raise SystemExit(7)"
        elif executable == "xwininfo.exe":
            if self.mode == "success":
                script = "print('  Width: 800\\n  Height: 600')"
            elif self.mode == "timeout":
                script = "import time; time.sleep(60)"
            elif self.mode == "zero_size":
                script = "print('  Width: 0\\n  Height: 600')"
            else:
                script = "import sys; print('unable to open display', file=sys.stderr); sys.exit(1)"
        else:
            raise AssertionError(f"Unexpected executable: {executable}")
        child = self.real_popen([sys.executable, "-B", "-c", script], **kwargs)
        self.children.append(child)
        return child

    def verify(self, timeout=2, display=97):
        report = runtime_tool.verify(self.runtime, self.dumpbin, "a" * 40,
                                     self.output, display, timeout)
        saved = json.loads((self.output / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, report)
        return report

    def test_parse_dependency_sections(self):
        text = ("  Image has the following dependencies:\r\n    libX11.dll\r\n"
                "    KERNEL32.dll\r\n  Image has the following delay load dependencies:\r\n"
                "    OPENGL32.dll\r\n    kernel32.DLL\r\n  Summary\r\n    junk.dll\r\n")
        self.assertEqual(runtime_tool.parse_dependencies(text),
                         ["libX11.dll", "KERNEL32.dll", "OPENGL32.dll"])

    def test_parse_rejects_unrecognized_output(self):
        with self.assertRaises(ValueError):
            runtime_tool.parse_dependencies("dumpbin failed unexpectedly")

    def test_mesa_can_import_symbols_from_server_executable(self):
        self.dependencies = "Image has the following dependencies:\n  vcxsrv.exe\n  Summary\n"
        report = self.verify()
        self.assertEqual(report["status"], "PASS", report)

    def test_parse_accepts_no_imports_image(self):
        self.assertEqual(runtime_tool.parse_dependencies("File Type: DLL\n\n  Summary\n  1000 .data\n"), [])

    def test_truncated_pe_rejected(self):
        for contents in (b"", b"MZ", b"MZ" + bytes(62), b"MZ" + bytes(254)):
            with self.subTest(length=len(contents)):
                target = self.runtime / "bad.dll"
                target.write_bytes(contents)
                with self.assertRaises(ValueError):
                    runtime_tool.pe_machine(target)

    def test_missing_required_executable_never_starts(self):
        for name in ("vcxsrv.exe", "xauth.exe", "xwininfo.exe"):
            with self.subTest(name=name):
                self.output = self.root / (name + " evidence")
                (self.runtime / name).unlink()
                report = self.verify()
                self.assertEqual(report["status"], "NOT_RUN")
                self.assertIn(name, json.dumps(report))
                self.assertFalse(self.children)
                pe_file(self.runtime / name)

    def test_rejects_32bit_dll_before_launch(self):
        pe_file(self.runtime / "wrong.dll", 0x14c)
        report = self.verify()
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("wrong.dll", json.dumps(report))
        self.assertFalse(any(Path(args[0]).name != "dumpbin.exe" for args, _ in self.commands))

    def test_missing_import_names_referrer(self):
        self.dependencies = "Image has the following dependencies:\n  missing.dll\n  Summary\n"
        report = self.verify()
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("missing.dll", json.dumps(report))
        self.assertIn("vcxsrv.exe", json.dumps(report))

    def test_dumpbin_failure_is_not_no_dependencies(self):
        self.dumpbin_exit = 3
        report = self.verify()
        step = next(s for s in report["steps"] if s["name"] == "dependencies")
        self.assertEqual(step["status"], "FAIL")
        self.assertEqual(step["exit_code"], 3)

    def test_local_system_and_api_set_resolution(self):
        pe_file(self.runtime / "LOCAL.dll")
        pe_file(self.system32 / "SYSTEM.dll")
        self.dependencies = ("Image has the following dependencies:\n  local.dll\n"
                             "  system.dll\n  api-ms-win-core-test-l1-1-0.dll\n  Summary\n")
        report = self.verify()
        self.assertEqual(report["status"], "PASS", report)
        data = json.loads((self.output / "dependencies.json").read_text())
        self.assertIn("system_contract", json.dumps(data))

    def test_success_requires_root_query_and_cleans_auth_and_processes(self):
        report = self.verify()
        self.assertEqual(report["status"], "PASS", report)
        self.assertTrue(all(child.poll() is not None for child in self.children))
        self.assertTrue(self.auth_paths)
        self.assertTrue(all(not path.exists() for path in self.auth_paths))
        self.assertTrue(any("-root" in args for args, _ in self.commands))
        for path in self.output.rglob("*"):
            if path.is_file():
                self.assertNotIn(self.cookie, path.read_text(errors="replace"))

    def test_client_failures_and_timeout_cleanup(self):
        for mode in ("client_failure", "timeout", "zero_size", "server_exit"):
            with self.subTest(mode=mode):
                self.mode = mode
                self.output = self.root / mode
                report = self.verify(timeout=0.7)
                self.assertEqual(report["status"], "FAIL", report)
                self.assertTrue(all(child.poll() is not None for child in self.children))
                self.assertTrue(all(not path.exists() for path in self.auth_paths))

    def test_occupied_port_does_not_touch_external_listener(self):
        with socket.socket() as listener:
            for candidate in range(24000, 24100):
                try:
                    listener.bind(("127.0.0.1", candidate))
                    break
                except OSError:
                    continue
            else:
                self.fail("No available port for controlled listener test")
            listener.listen()
            port = listener.getsockname()[1]
            report = self.verify(display=port - 6000)
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("port", json.dumps(report).lower())
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                pass
            self.assertFalse(self.auth_paths)

    def test_child_environment_is_isolated_without_parent_changes(self):
        dirty = {"DISPLAY": "bad", "XAUTHORITY": "bad", "XLOCALEDIR": "bad",
                 "XKEYSYMDB": "bad", "XERRORDB": "bad", "XKB_CONFIG_ROOT": "bad",
                 "PATH": "bad", "display": "bad"}
        with patch.dict(os.environ, dirty):
            original = dict(os.environ)
            report = self.verify()
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual(dict(os.environ), original)
            for args, env in self.commands:
                self.assertEqual(env["PATH"], str(self.runtime) + os.pathsep + str(self.system32))
                self.assertNotIn("DISPLAY", env)
                self.assertNotIn("display", env)
                self.assertNotIn("XLOCALEDIR", env)
                if Path(args[0]).name == "xwininfo.exe":
                    self.assertNotEqual(env["XAUTHORITY"], "bad")

    def test_output_must_be_fresh_and_not_overlap_runtime(self):
        self.output.mkdir()
        marker = self.output / "result.json"
        marker.write_text("previous evidence")
        with self.assertRaises(ValueError):
            self.verify()
        self.assertEqual(marker.read_text(), "previous evidence")
        for output in (self.runtime, self.runtime / "evidence", self.root):
            with self.subTest(output=output), self.assertRaises(ValueError):
                runtime_tool.verify(self.runtime, self.dumpbin, "a" * 40, output, 97, 1)

    def test_cli_requires_source_commit(self):
        result = self.real_popen([sys.executable, "-B", str(MODULE), "--runtime", str(self.runtime),
                                 "--dumpbin", str(self.dumpbin), "--output", str(self.output)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = result.communicate(timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"--source-commit", stderr)

    def test_nonfinite_timeout_preserves_valid_json_failure_evidence(self):
        def reject_constant(value):
            self.fail("Invalid JSON number: " + value)

        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(timeout=value):
                self.output = self.root / ("invalid timeout " + str(value))
                report = runtime_tool.verify(self.runtime, self.dumpbin, "a" * 40,
                                             self.output, 97, value)
                self.assertEqual(report["status"], "NOT_RUN")
                json.loads((self.output / "result.json").read_text(), parse_constant=reject_constant)
                self.assertFalse(self.children)

    def test_authentication_failure_and_timeout_redact_diagnostic_secrets(self):
        for mode in ("auth_failure", "auth_timeout"):
            with self.subTest(mode=mode):
                self.mode = mode
                self.output = self.root / mode
                report = self.verify(timeout=0.3)
                self.assertEqual(report["status"], "FAIL", report)
                self.assertTrue(all(child.poll() is not None for child in self.children))
                self.assertTrue(all(not path.exists() for path in self.auth_paths))
                self.assertTrue(self.cookie)
                for path in self.output.rglob("*"):
                    if path.is_file():
                        self.assertNotIn(self.cookie, path.read_text(errors="replace"))
                self.assertIn("<redacted>", (self.output / "xauth.stdout.log").read_text())


@unittest.skipUnless(os.environ.get("VCXSRV_TEST_RUNTIME") == "1",
                     "set VCXSRV_TEST_RUNTIME=1 for authenticated desktop integration")
class RuntimeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        required = ("VCXSRV_RUNTIME_DIR", "VCXSRV_DUMPBIN", "VCXSRV_SOURCE_COMMIT")
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            raise AssertionError("Runtime integration enabled but missing: " + ", ".join(missing))
        cls.runtime = Path(os.environ["VCXSRV_RUNTIME_DIR"])
        cls.dumpbin = Path(os.environ["VCXSRV_DUMPBIN"])
        cls.commit = os.environ["VCXSRV_SOURCE_COMMIT"]

    def test_real_runtime_then_missing_dll_and_path_with_spaces(self):
        self.assertIsNotNone(runtime_tool)
        with tempfile.TemporaryDirectory(prefix="vcxsrv integration ") as directory:
            root = Path(directory)
            original = runtime_tool.verify(self.runtime, self.dumpbin, self.commit,
                                           root / "original evidence", 97, 30)
            self.assertEqual(original["status"], "PASS", original)
            copied = root / "runtime with spaces"
            shutil.copytree(self.runtime, copied)
            missing_dll = copied / "libX11.dll"
            self.assertTrue(missing_dll.is_file())
            missing_dll.unlink()
            missing = runtime_tool.verify(copied, self.dumpbin, self.commit,
                                          root / "missing evidence", 97, 30)
            self.assertEqual(missing["status"], "FAIL", missing)
            self.assertIn("libX11.dll", json.dumps(missing))
            shutil.copy2(self.runtime / "libX11.dll", missing_dll)
            spaces = runtime_tool.verify(copied, self.dumpbin, self.commit,
                                         root / "spaces evidence", 97, 30)
            self.assertEqual(spaces["status"], "PASS", spaces)


if __name__ == "__main__":
    unittest.main()
