"""Run real XKB request validation code under MSVC AddressSanitizer.

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
class XkbRequestsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: run from an x64 MSVC developer environment")
        cls.directory = tempfile.TemporaryDirectory(prefix="vcxsrv_xkb_")
        cls.addClassCleanup(cls.directory.cleanup)
        work = Path(cls.directory.name)
        cls.exe = work / "xkb_requests.exe"
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
                   str(ROOT / "tools/tests/native/xkb_requests.c"),
                   "/Fe:" + str(cls.exe), "/link", "/OPT:REF", "/INCREMENTAL:NO"]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                errors="replace", timeout=120)
        print("COMPILE " + subprocess.list2cmdline(command), flush=True)
        print(result.stdout + result.stderr, flush=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def run_case(self, name):
        result = subprocess.run([str(self.exe), name], capture_output=True, text=True,
                                errors="replace", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS " + name, result.stdout)

    def test_type_level_max(self):
        self.run_case("type-level-max")

    def test_type_level_over(self):
        self.run_case("type-level-over")

    def test_type_count_max(self):
        self.run_case("type-count-max")

    def test_type_count_over(self):
        self.run_case("type-count-over")

    def test_type_short(self):
        self.run_case("type-short")

    def test_type_short_swapped(self):
        self.run_case("type-short-swapped")

    def test_type_map_short(self):
        self.run_case("type-map-short")

    def test_type_preserve_short(self):
        self.run_case("type-preserve-short")

    def test_type_valid(self):
        self.run_case("type-valid")

    def test_type_valid_swapped(self):
        self.run_case("type-valid-swapped")

    def test_sym_short(self):
        self.run_case("sym-short")

    def test_sym_data_short(self):
        self.run_case("sym-data-short")

    def test_sym_empty(self):
        self.run_case("sym-empty")

    def test_sym_valid(self):
        self.run_case("sym-valid")

    def test_modifier_short(self):
        self.run_case("modifier-short")

    def test_modifier_valid(self):
        self.run_case("modifier-valid")

    def test_action_count_short(self):
        self.run_case("action-count-short")

    def test_action_data_short(self):
        self.run_case("action-data-short")

    def test_action_zero(self):
        self.run_case("action-zero")

    def test_action_valid(self):
        self.run_case("action-valid")

    def test_behavior_short(self):
        self.run_case("behavior-short")

    def test_behavior_valid(self):
        self.run_case("behavior-valid")

    def test_vmods_short(self):
        self.run_case("vmods-short")

    def test_vmods_valid(self):
        self.run_case("vmods-valid")

    def test_explicit_short(self):
        self.run_case("explicit-short")

    def test_explicit_valid(self):
        self.run_case("explicit-valid")

    def test_vmodmap_short(self):
        self.run_case("vmodmap-short")

    def test_vmodmap_valid(self):
        self.run_case("vmodmap-valid")

    def test_compat_overflow(self):
        self.run_case("compat-overflow")

    def test_compat_reuse(self):
        self.run_case("compat-reuse")

    def test_compat_truncate(self):
        self.run_case("compat-truncate")

    def test_compat_skipped(self):
        self.run_case("compat-skipped")

    def test_compat_grow(self):
        self.run_case("compat-grow")

    def test_overlay_index(self):
        self.run_case("overlay-index")

    def test_overlay_alloc(self):
        self.run_case("overlay-alloc")

    def test_overlay_row_alloc(self):
        self.run_case("overlay-row-alloc")

    def test_overlay_valid(self):
        self.run_case("overlay-valid")

    def test_shape_primary(self):
        self.run_case("shape-primary")

    def test_shape_approx(self):
        self.run_case("shape-approx")

    def test_shape_sentinel(self):
        self.run_case("shape-sentinel")

    def test_shape_valid(self):
        self.run_case("shape-valid")

    def test_color_base(self):
        self.run_case("color-base")

    def test_color_label(self):
        self.run_case("color-label")

    def test_alias_short(self):
        self.run_case("alias-short")

    def test_alias_valid(self):
        self.run_case("alias-valid")


if __name__ == "__main__":
    unittest.main()
