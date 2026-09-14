"""Run real RANDR provider property code under MSVC AddressSanitizer.

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
class RandrProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: run from an x64 MSVC developer environment")
        cls.directory = tempfile.TemporaryDirectory(prefix="vcxsrv_randr_")
        cls.addClassCleanup(cls.directory.cleanup)
        work = Path(cls.directory.name)
        cls.exe = work / "randr_provider.exe"
        includes = [".", "include", "third_party/pthreads",
                    "third_party/graphics/pixman/pixman",
                    "third_party/graphics/mesalib/include", "include/gl/include",
                    "src/xorg-server", "src/xorg-server/include", "src/xorg-server/glx",
                    "src/xorg-server/mi", "src/xorg-server/render", "src/xorg-server/Xext",
                    "src/xorg-server/miext/damage", "src/xorg-server/present"]
        defines = ["WIN32", "_WINDOWS", "WINDOWS", "_MBCS", "__i386__", "__MINGW32__",
                   "_POSIX_", "X_NOT_POSIX", "_TIMEVAL_DEFINED", "mode_t=int", "__STDC__",
                   "FAKEIT", "HAVE_CONFIG_H", "_BSD_SOURCE", "_WIN32_WINNT=0x0601",
                   "XKB_IN_SERVER", "XFree86Server", "HAVE_DIX_CONFIG_H", "PIXMAN_API="]
        command = [compiler, "/nologo", "/std:c11", "/Od", "/Gy", "/Gw", "/Zc:inline", "/MD", "/Zi",
                   "/fsanitize=address", *["/I" + str(ROOT / p) for p in includes],
                   *["/D" + d for d in defines],
                   str(ROOT / "tools/tests/native/randr_provider.c"),
                   "/Fe:" + str(cls.exe), "/link", "/OPT:REF", "/INCREMENTAL:NO"]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                errors="replace", timeout=120)
        print("COMPILE " + subprocess.list2cmdline(command), flush=True)
        print(result.stdout + result.stderr, flush=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def run_case(self, name, format, mode, pending):
        result = subprocess.run([str(self.exe), name, str(format), str(mode), str(pending)],
                                capture_output=True, text=True, errors="replace", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS " + name, result.stdout)


def _case(name, format, mode, pending):
    def test(self):
        self.run_case(name, format, mode, pending)
    return test


# Separate cases make every format, mode, and current/pending branch visible.
for _name in ("overflow", "boundary", "valid", "zero", "new_overflow"):
    for _format in (8, 16, 32):
        for _mode_name, _mode in (("replace", 0), ("prepend", 1), ("append", 2)):
            for _pending in (0, 1):
                setattr(RandrProviderTests,
                        f"test_{_name}_{_format}_{_mode_name}_{'pending' if _pending else 'current'}",
                        _case(_name, _format, _mode, _pending))


if __name__ == "__main__":
    unittest.main()
