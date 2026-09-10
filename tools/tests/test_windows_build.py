"""Integration checks for the Windows build entry point (no compilation)."""
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts/build/buildall.ps1"
POWERSHELL = shutil.which("powershell.exe")


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "requires Windows PowerShell")
class WindowsBuildTests(unittest.TestCase):
    def run_check(self, *args):
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(BUILD_SCRIPT), "-CheckOnly", *args],
            cwd=ROOT.parent, capture_output=True, text=True,
        )

    def test_invalid_explicit_python_is_not_silently_ignored(self):
        result = self.run_check("-PythonPath", str(ROOT / "missing-python.exe"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-python.exe", result.stdout + result.stderr)

    def test_preflight_does_not_compile_or_generate_sources(self):
        # Enabled on a provisioned machine; detects accidentally falling through
        # from preflight into generation/build steps.
        if not os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"):
            self.skipTest("set VCXSRV_TEST_LOCAL_TOOLS=1 for local toolchain preflight")
        watched = [ROOT / "tools/mhmake/Release64/mhmake.exe",
                   ROOT / "tools/mhmake/Release64/mhmakelexer.cpp",
                   ROOT / "third_party/openssl/release64/configdata.pm"]
        before = [(p.exists(), p.stat().st_mtime_ns if p.exists() else None) for p in watched]
        with tempfile.TemporaryDirectory(prefix="vcxsrv report ") as directory:
            report = Path(directory) / "environment.json"
            result = self.run_check("-EnvironmentReport", str(report))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(report.is_file())
            self.assertEqual(before, [(p.exists(), p.stat().st_mtime_ns if p.exists() else None)
                                      for p in watched])

    def test_check_only_reports_selected_python(self):
        if not os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"):
            self.skipTest("requires local toolchain")
        with tempfile.TemporaryDirectory(prefix="vcxsrv report ") as directory:
            report = Path(directory) / "environment.json"
            result = self.run_check("-PythonPath", sys.executable,
                                    "-EnvironmentReport", str(report))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(report.read_text(encoding="utf-8-sig"))
            self.assertEqual(set(data), {
                "schema_version", "source_commit", "target", "host", "tools",
                "python_packages",
            })
            self.assertEqual(data["schema_version"], 1)
            self.assertRegex(data["source_commit"], r"^[0-9a-f]{40}$")
            self.assertEqual(data["target"], {
                "architecture": "x64", "configuration": "Release",
            })
            self.assertTrue(data["host"]["windows_version"])
            self.assertTrue(data["host"]["powershell_version"])
            self.assertEqual(Path(data["tools"]["python"]["path"]), Path(sys.executable))
            self.assertTrue(data["tools"]["python"]["version"])
            for name in ("cl", "msbuild", "dumpbin", "flex", "bison", "msvc", "sdk"):
                self.assertIn(name, data["tools"])
                self.assertTrue(data["tools"][name]["path"])
                self.assertIn("version", data["tools"][name])
            self.assertIsNone(data["tools"]["flex"]["version"])
            expected_packages = {
                name: importlib.metadata.version(name)
                for name in ("lxml", "mako", "PyYAML")
            }
            self.assertEqual(data["python_packages"], expected_packages)

    def test_build_tool_report_omits_tools_not_selected_for_the_stage(self):
        if not os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"):
            self.skipTest("requires local toolchain")
        with tempfile.TemporaryDirectory(prefix="vcxsrv report ") as directory:
            report = Path(directory) / "environment.json"
            result = self.run_check("-Stage", "BuildTool", "-PythonPath", sys.executable,
                                    "-EnvironmentReport", str(report))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(report.read_text(encoding="utf-8-sig"))
            self.assertTrue({"python", "cl", "msbuild", "dumpbin", "flex", "bison",
                             "msvc", "sdk"} <= data["tools"].keys())
            self.assertTrue({"perl", "nasm", "gperf", "jom"}.isdisjoint(data["tools"]))

    def test_relative_report_path_uses_powershell_location(self):
        if not os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"):
            self.skipTest("requires local toolchain")
        script = str(BUILD_SCRIPT).replace("'", "''")
        with tempfile.TemporaryDirectory(prefix="vcxsrv report parent ") as directory:
            caller = Path(directory) / "caller with spaces"
            caller.mkdir()
            escaped_caller = str(caller).replace("'", "''")
            code = f"""
Set-Location -LiteralPath '{escaped_caller}'
& '{script}' -CheckOnly -Stage BuildTool -PythonPath '{sys.executable}' -EnvironmentReport 'evidence/environment.json'
if ($LASTEXITCODE -ne 0) {{ exit $LASTEXITCODE }}
"""
            result = subprocess.run([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
                                     "-Command", code], cwd=directory,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((caller / "evidence/environment.json").is_file())
            self.assertFalse((Path(directory) / "evidence/environment.json").exists())

    def test_generator_directory_with_spaces(self):
        if not os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"):
            self.skipTest("requires local native generators")
        source = Path(os.environ.get("VCXSRV_TEST_FLEX_DIR", r"D:\SoftWare\win_flex_bison-2.5.25"))
        if not (source / "win_flex.exe").is_file():
            self.skipTest("set VCXSRV_TEST_FLEX_DIR to WinFlexBison")
        with tempfile.TemporaryDirectory(prefix="vcxsrv tools with spaces ") as directory:
            for name in ("win_flex.exe", "win_bison.exe"):
                shutil.copy2(source / name, Path(directory) / name)
            result = self.run_check("-Stage", "BuildTool", "-WinFlexBisonPath", directory)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_environment_and_location_restored_after_success_and_failure(self):
        if not os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"):
            self.skipTest("requires local toolchain")
        script = str(BUILD_SCRIPT).replace("'", "''")
        for failure in (False, True):
            with self.subTest(failure=failure):
                with tempfile.TemporaryDirectory(prefix="vcxsrv report ") as directory:
                    report = str(Path(directory) / "environment.json").replace("'", "''")
                    missing = str(ROOT / "missing-python.exe").replace("'", "''")
                    args = f"-PythonPath '{missing}'" if failure else ""
                    expect_report = str(not failure).lower()
                    code = f"""
$before = (Get-ChildItem Env: | Sort-Object Name | ConvertTo-Json -Compress)
$directory = (Get-Location).Path
try {{ & '{script}' -CheckOnly -Stage BuildTool -EnvironmentReport '{report}' {args} }} catch {{
    if (-not ${str(failure).lower()}) {{ throw }}
}}
$after = (Get-ChildItem Env: | Sort-Object Name | ConvertTo-Json -Compress)
if ($before -cne $after) {{ throw 'Build script leaked environment changes' }}
if ($directory -ne (Get-Location).Path) {{ throw 'Build script changed working directory' }}
if ((Test-Path -LiteralPath '{report}') -ne ${expect_report}) {{ throw 'Unexpected environment report state' }}
exit 0
"""
                    result = subprocess.run([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
                                             "-Command", code], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
