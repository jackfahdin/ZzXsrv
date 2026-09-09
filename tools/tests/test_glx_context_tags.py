"""Run real GLX dispatch/mapping code under MSVC AddressSanitizer.

Set VCXSRV_TEST_LOCAL_TOOLS=1 in an x64 Visual Studio developer environment.
No network connections or dependency installation are performed.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt" and os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"),
                     "enable local tools in an x64 MSVC developer environment")
class GlxContextTagsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: run from an x64 MSVC developer environment")
        cls.directory = tempfile.TemporaryDirectory(prefix="vcxsrv_glx_")
        cls.addClassCleanup(cls.directory.cleanup)
        work = Path(cls.directory.name)
        cls.exe = work / "glx_context_tags.exe"
        includes = [".", "include", "pthreads", "pixman/pixman", "mesalib/include",
                    "gl/include", "xorg-server", "xorg-server/include", "xorg-server/glx",
                    "xorg-server/mi", "xorg-server/render", "xorg-server/Xext",
                    "xorg-server/miext/damage"]
        defines = ["WIN32", "_WINDOWS", "WINDOWS", "_MBCS", "__i386__", "__MINGW32__",
                   "_POSIX_", "X_NOT_POSIX", "_TIMEVAL_DEFINED", "mode_t=int", "__STDC__",
                   "FAKEIT", "HAVE_CONFIG_H", "_BSD_SOURCE", "_WIN32_WINNT=0x0601",
                   "XKB_IN_SERVER", "XFree86Server", "HAVE_DIX_CONFIG_H", "PIXMAN_API="]
        command = [compiler, "/nologo", "/std:c11", "/Od", "/Gy", "/MD", "/Zi",
                   "/fsanitize=address", *["/I" + str(ROOT / p) for p in includes],
                   *["/D" + d for d in defines],
                   str(ROOT / "tools/tests/native/glx_context_tags.c"),
                   "/Fe:" + str(cls.exe), "/link", "/OPT:REF", "/INCREMENTAL:NO"]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                errors="replace", timeout=120)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def run_case(self, name):
        result = subprocess.run([str(self.exe), name], capture_output=True, text=True,
                                errors="replace", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS " + name, result.stdout)

    def test_full_array_context_switch(self):
        self.run_case("switch")

    def test_full_array_swapped_context_switch(self):
        self.run_case("switch-swapped")

    def test_growth_preserves_existing_contexts(self):
        self.run_case("growth")

    def test_unchanged_context_and_release(self):
        self.run_case("same-and-release")

    def test_lose_failure_preserves_old_context(self):
        self.run_case("lose-failure")

    def test_make_failure_releases_old_and_new_tags(self):
        self.run_case("make-failure")

    def test_allocation_failure_preserves_existing_contexts(self):
        self.run_case("allocation-failure")

    def test_invalid_context_and_tag_rejected(self):
        self.run_case("invalid-ids")


if __name__ == "__main__":
    unittest.main()
