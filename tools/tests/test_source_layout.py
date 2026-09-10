"""Check repository discovery from a relocated component and an unrelated cwd."""
import gzip
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SourceLayoutTests(unittest.TestCase):
    @unittest.skipUnless(
        os.name == "nt" and (ROOT / "tools/mhmake/Release64/mhmake.exe").is_file()
        and (ROOT / "third_party/xorg/bdftopcf/obj64/release/bdftopcf.exe").is_file(),
        "build x64 mhmake and font tools first")
    def test_relocated_font_tool_runs_in_mhmake_pipeline(self):
        # cmd.exe parses an unquoted executable's forward slash as a delimiter.
        # Exercise the actual component variable and pipeline, not just path existence.
        with tempfile.TemporaryDirectory(prefix="font_pipeline_", dir=ROOT / "tools/tests") as directory:
            work = Path(directory)
            (work / "makefile").write_text(
                'all: font.gz\n'
                'font.gz:\n'
                '\t$(BDFTOPCF) -t $(COMPONENT_XORG_SERVER_DIR)\\fonts.src\\75dpi\\lutBS08.bdf '
                '| $(BUILD_NATIVE) gzip > font.gz\n', encoding="ascii")
            environment = os.environ.copy()
            environment.update(MHMAKECONF=str(ROOT), IS64="1", PYTHON3=sys.executable)
            environment["PATH"] = str(ROOT / "third_party/zlib/obj64/release") + os.pathsep + environment["PATH"]
            result = subprocess.run(
                [str(ROOT / "tools/mhmake/Release64/mhmake.exe"), "-P1", "-C", str(work)],
                env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(gzip.decompress((work / "font.gz").read_bytes())[:4], b"\x01fcp")

    def test_mesa_version_retains_repository_revision(self):
        revision = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()[:10]
        generator = ROOT / "third_party/graphics/mesalib/bin/git_sha1_gen.py"
        environment = os.environ.copy()
        environment.pop("MESA_GIT_SHA1_OVERRIDE", None)
        with tempfile.TemporaryDirectory(prefix="zzxsrv version ") as directory:
            output = Path(directory) / "git_sha1.h"
            subprocess.run([sys.executable, "-B", str(generator), "--output", str(output)],
                           cwd=directory, env=environment, check=True,
                           capture_output=True, text=True)
            self.assertEqual(output.read_text(),
                             '#define MESA_GIT_SHA1 " (git-' + revision + ')"')


if __name__ == "__main__":
    unittest.main()
