"""Targeted ASan tests for XKB auxiliary compatibility fixes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt" and os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"),
                     "enable local tools in an x64 MSVC developer environment")
class XkbAuxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: run from an x64 MSVC developer environment")
        cls.directory = tempfile.TemporaryDirectory(prefix="vcxsrv_xkb_aux_")
        cls.addClassCleanup(cls.directory.cleanup)
        work = Path(cls.directory.name)
        includes = [".", "include", "third_party/pthreads",
                    "third_party/graphics/pixman/pixman",
                    "third_party/graphics/mesalib/include", "include/gl/include",
                    "src/xorg-server", "src/xorg-server/include", "src/xorg-server/xkb",
                    "src/xorg-server/mi", "src/xorg-server/render"]
        defines = ["WIN32", "_WINDOWS", "WINDOWS", "_MBCS", "__i386__", "__MINGW32__",
                   "_POSIX_", "X_NOT_POSIX", "_TIMEVAL_DEFINED", "mode_t=int", "__STDC__",
                   "FAKEIT", "HAVE_CONFIG_H", "_BSD_SOURCE", "_WIN32_WINNT=0x0601",
                   "XKB_IN_SERVER", "XFree86Server", "HAVE_DIX_CONFIG_H", "PIXMAN_API="]
        cls.executables = {}
        for stem in ("alloc", "text", "concat"):
            exe = work / ("xkb_aux_" + stem + ".exe")
            command = [compiler, "/nologo", "/std:c11", "/Od", "/Gy", "/Gw", "/Zc:inline",
                       "/MD", "/Zi", "/fsanitize=address",
                       *["/I" + str(ROOT / p) for p in includes], *["/D" + d for d in defines],
                       str(ROOT / ("tools/tests/native/xkb_aux_" + stem + ".c")),
                       "/Fe:" + str(exe), "/link", "/OPT:REF", "/INCREMENTAL:NO"]
            result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                    errors="replace", timeout=120)
            print("COMPILE " + subprocess.list2cmdline(command), flush=True)
            print(result.stdout + result.stderr, flush=True)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            cls.executables[stem] = exe

    def run_case(self, stem, name):
        result = subprocess.run([str(self.executables[stem]), name], capture_output=True,
                                text=True, errors="replace", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS " + name, result.stdout)

    def test_section_doodad_capacity(self): self.run_case("alloc", "section-capacity")
    def test_global_doodad_capacity(self): self.run_case("alloc", "global-capacity")
    def test_cfile_normal_name(self): self.run_case("text", "normal-name")
    def test_cfile_boundary_index(self): self.run_case("text", "boundary-index")
    def test_concat_normal(self): self.run_case("concat", "normal")
    def test_concat_null_first(self): self.run_case("concat", "null-first")
    def test_concat_null_second(self): self.run_case("concat", "null-second")
    def test_concat_empty(self): self.run_case("concat", "empty")
    def test_concat_realloc_failure(self): self.run_case("concat", "realloc-failure")


if __name__ == "__main__":
    unittest.main()
