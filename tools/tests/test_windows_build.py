"""Integration checks for the Windows build entry point (no compilation)."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
POWERSHELL = shutil.which("powershell.exe")


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "requires Windows PowerShell")
class WindowsBuildTests(unittest.TestCase):
    def run_check(self, *args):
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(ROOT / "buildall.ps1"), "-CheckOnly", *args],
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
                   ROOT / "openssl/release64/configdata.pm"]
        before = [(p.exists(), p.stat().st_mtime_ns if p.exists() else None) for p in watched]
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, [(p.exists(), p.stat().st_mtime_ns if p.exists() else None)
                                  for p in watched])

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
        script = str(ROOT / "buildall.ps1").replace("'", "''")
        for failure in (False, True):
            with self.subTest(failure=failure):
                args = "-PythonPath 'missing-python.exe'" if failure else ""
                code = f"""
$before = (Get-ChildItem Env: | Sort-Object Name | ConvertTo-Json -Compress)
$directory = (Get-Location).Path
try {{ & '{script}' -CheckOnly -Stage BuildTool {args} }} catch {{
    if (-not ${str(failure).lower()}) {{ throw }}
}}
$after = (Get-ChildItem Env: | Sort-Object Name | ConvertTo-Json -Compress)
if ($before -cne $after) {{ throw 'Build script leaked environment changes' }}
if ($directory -ne (Get-Location).Path) {{ throw 'Build script changed working directory' }}
exit 0
"""
                result = subprocess.run([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
                                         "-Command", code], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
