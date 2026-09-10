"""Check repository discovery from a relocated component and an unrelated cwd."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SourceLayoutTests(unittest.TestCase):
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
