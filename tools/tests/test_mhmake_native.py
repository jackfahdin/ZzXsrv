"""Regression checks at the mhmake -> cmd -> native generator boundary."""
import gzip
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import venv

ROOT = Path(__file__).resolve().parents[2]
MHMAKE = ROOT / "tools/mhmake/Release64/mhmake.exe"


@unittest.skipUnless(os.name == "nt" and MHMAKE.is_file(), "build x64 mhmake first")
class MhmakeNativeTests(unittest.TestCase):
    def test_redirected_python_with_space_in_interpreter_path(self):
        # Direct quoted executable names break legacy mhmake's shell parser.
        # Run the actual recipes/launcher with a real Python venv in a spaced path.
        with tempfile.TemporaryDirectory(prefix="vcxsrv_mhmake_", dir=ROOT / "tools/tests") as directory:
            work = Path(directory)
            interpreter = work / "python environment"
            venv.create(interpreter, with_pip=False)
            (work / "input.bin").write_bytes(bytes(range(256)))
            (work / "version-data").mkdir()
            (work / "version-data/VERSION").write_text("25.1.0\n", encoding="ascii")
            (work / "makefile").write_text(
                'all: font.gz version.txt piped.gz\n'
                'font.gz: input.bin\n'
                '\t$(BUILD_NATIVE) gzip < input.bin > font.gz\n'
                'version.txt:\n'
                '\t$(PYTHON) --version > version.txt\n'
                'piped.gz:\n'
                '\t$(PYTHON) -c "import sys; sys.stdout.write(\'pipeline\')" | $(BUILD_NATIVE) gzip > piped.gz\n'
                'PACKAGE_VERSION:=$(strip $(shell type $(subst /,\\,version-data/VERSION)))\n'
                'all:\n'
                '\techo $(PACKAGE_VERSION) > package.txt\n', encoding="ascii")
            environment = os.environ.copy()
            environment.update(MHMAKECONF=str(ROOT), IS64="1",
                               PYTHON3=str(interpreter / "Scripts/python.exe"))
            result = subprocess.run([str(MHMAKE), "-P1", "-C", str(work)],
                                    env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(gzip.decompress((work / "font.gz").read_bytes()), bytes(range(256)))
            self.assertEqual(gzip.decompress((work / "piped.gz").read_bytes()), b"pipeline")
            self.assertTrue((work / "version.txt").read_text().startswith("Python 3."))
            self.assertEqual((work / "package.txt").read_text().strip(), "25.1.0")

    def test_failed_generator_returns_failure_to_mhmake(self):
        # A batch wrapper must not hide its child's nonzero exit status.
        with tempfile.TemporaryDirectory(prefix="vcxsrv_mhmake_", dir=ROOT / "tools/tests") as directory:
            work = Path(directory)
            (work / "makefile").write_text(
                'all:\n\t$(PYTHON) -c "raise SystemExit(7)"\n', encoding="ascii")
            environment = os.environ.copy()
            import sys
            environment.update(MHMAKECONF=str(ROOT), IS64="1", PYTHON3=sys.executable)
            result = subprocess.run([str(MHMAKE), "-P1", "-C", str(work)],
                                    env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("SystemExit(7)", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
