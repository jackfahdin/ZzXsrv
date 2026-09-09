"""Run real XFIXES disconnect handler code under MSVC AddressSanitizer.

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
class XfixesDisconnectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: run from an x64 MSVC developer environment")
        cls.directory = tempfile.TemporaryDirectory(prefix="vcxsrv_xfixes_")
        cls.addClassCleanup(cls.directory.cleanup)
        work = Path(cls.directory.name)
        cls.exe = work / "xfixes_disconnect.exe"
        includes = [".", "include", "pthreads", "pixman/pixman", "mesalib/include",
                    "gl/include", "xorg-server", "xorg-server/include", "xorg-server/glx",
                    "xorg-server/mi", "xorg-server/render", "xorg-server/Xext",
                    "xorg-server/miext/damage", "xorg-server/present", "xorg-server/Xi", "xorg-server/xfixes"]
        defines = ["WIN32", "_WINDOWS", "WINDOWS", "_MBCS", "__i386__", "__MINGW32__",
                   "_POSIX_", "X_NOT_POSIX", "_TIMEVAL_DEFINED", "mode_t=int", "__STDC__",
                   "FAKEIT", "HAVE_CONFIG_H", "_BSD_SOURCE", "_WIN32_WINNT=0x0601",
                   "XKB_IN_SERVER", "XFree86Server", "HAVE_DIX_CONFIG_H", "PIXMAN_API="]
        command = [compiler, "/nologo", "/std:c11", "/Od", "/Gy", "/MD", "/Zi",
                   "/fsanitize=address", *["/I" + str(ROOT / p) for p in includes],
                   *["/D" + d for d in defines],
                   str(ROOT / "tools/tests/native/xfixes_disconnect.c"),
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

    def test_normal_set_get(self):
        self.run_case("normal")

    def test_swapped_set_get(self):
        self.run_case("swapped")

    def test_short_request_preserves_mode(self):
        self.run_case("short")

    def test_swapped_short_request_preserves_mode(self):
        self.run_case("short-swapped")

    def test_long_request_preserves_mode(self):
        self.run_case("long")

    def test_swapped_long_request_preserves_mode(self):
        self.run_case("long-swapped")

    def test_short_request_does_not_read_past_buffer(self):
        self.run_case("short-bounds")

    def test_swapped_short_request_does_not_read_past_buffer(self):
        self.run_case("short-bounds-swapped")


if __name__ == "__main__":
    unittest.main()
