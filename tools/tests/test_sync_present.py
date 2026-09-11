"""Targeted ASan tests for SYNC/PRESENT/screensaver fixes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt" and os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"),
                     "enable local tools in an x64 MSVC developer environment")
class SyncPresentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: run from an x64 MSVC developer environment")
        cls.directory = tempfile.TemporaryDirectory(prefix="vcxsrv_sync_present_")
        cls.addClassCleanup(cls.directory.cleanup)
        work = Path(cls.directory.name)
        includes = [".", "include", "third_party/pthreads",
                    "third_party/graphics/pixman/pixman",
                    "third_party/graphics/mesalib/include", "include/gl/include",
                    "src/xorg-server", "src/xorg-server/include", "src/xorg-server/xkb",
                    "src/xorg-server/mi", "src/xorg-server/render", "src/xorg-server/Xext", "src/xorg-server/Xi", "src/xorg-server/present", "src/xorg-server/miext/sync", "src/xorg-server/randr", "src/xorg-server/dri3", "src/xorg-server/miext/damage"]
        includes.append("src/xorg-server/xfixes")
        defines = ["WIN32", "_WINDOWS", "WINDOWS", "_MBCS", "__i386__", "__MINGW32__",
                   "_POSIX_", "X_NOT_POSIX", "_TIMEVAL_DEFINED", "mode_t=int", "__STDC__",
                   "FAKEIT", "HAVE_CONFIG_H", "_BSD_SOURCE", "_WIN32_WINNT=0x0601",
                   "XKB_IN_SERVER", "XFree86Server", "HAVE_DIX_CONFIG_H", "PIXMAN_API="]
        cls.executables = {}
        for stem in ("sync_lifecycle", "present_notifies", "saver_lifetime"):
            exe = work / (stem + ".exe")
            command = [compiler, "/nologo", "/std:c11", "/Od", "/Gy", "/Gw", "/Zc:inline",
                       "/MD", "/Zi", "/fsanitize=address",
                       *["/I" + str(ROOT / p) for p in includes], *["/D" + d for d in defines],
                       str(ROOT / ("tools/tests/native/" + stem + ".c")),
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

    def test_sync_lifecycle_counter_shared(self):
        self.run_case("sync_lifecycle","counter-shared")

    def test_sync_lifecycle_fence_shared(self):
        self.run_case("sync_lifecycle","fence-shared")

    def test_sync_lifecycle_counter_alarm(self):
        self.run_case("sync_lifecycle","counter-alarm")

    def test_sync_lifecycle_counter_no_fire(self):
        self.run_case("sync_lifecycle","counter-no-fire")

    def test_sync_lifecycle_fence_no_fire(self):
        self.run_case("sync_lifecycle","fence-no-fire")

    def test_sync_lifecycle_destroy_counter_shared(self):
        self.run_case("sync_lifecycle","destroy-counter-shared")

    def test_sync_lifecycle_destroy_fence_shared(self):
        self.run_case("sync_lifecycle","destroy-fence-shared")

    def test_sync_lifecycle_destroy_counter_single(self):
        self.run_case("sync_lifecycle","destroy-counter-single")

    def test_sync_lifecycle_destroy_fence_single(self):
        self.run_case("sync_lifecycle","destroy-fence-single")

    def test_sync_lifecycle_await_live(self):
        self.run_case("sync_lifecycle","await-live")

    def test_sync_lifecycle_await_destroying(self):
        self.run_case("sync_lifecycle","await-destroying")

    def test_sync_lifecycle_await_null(self):
        self.run_case("sync_lifecycle","await-null")

    def test_sync_lifecycle_counter_empty(self):
        self.run_case("sync_lifecycle","counter-empty")

    def test_sync_lifecycle_fence_empty(self):
        self.run_case("sync_lifecycle","fence-empty")

    def test_present_notifies_lookup_first(self):
        self.run_case("present_notifies","lookup-first")

    def test_present_notifies_lookup_second(self):
        self.run_case("present_notifies","lookup-second")

    def test_present_notifies_lookup_third(self):
        self.run_case("present_notifies","lookup-third")

    def test_present_notifies_alloc_first(self):
        self.run_case("present_notifies","alloc-first")

    def test_present_notifies_alloc_second(self):
        self.run_case("present_notifies","alloc-second")

    def test_present_notifies_alloc_third(self):
        self.run_case("present_notifies","alloc-third")

    def test_present_notifies_success_one(self):
        self.run_case("present_notifies","success-one")

    def test_present_notifies_success_three(self):
        self.run_case("present_notifies","success-three")

    def test_present_notifies_clear_window(self):
        self.run_case("present_notifies","clear-window")

    def test_saver_lifetime_no_private(self):
        self.run_case("saver_lifetime","no-private")

    def test_saver_lifetime_no_window_no_attr(self):
        self.run_case("saver_lifetime","no-window-no-attr")

    def test_saver_lifetime_old_window_release(self):
        self.run_case("saver_lifetime","old-window-release")

    def test_saver_lifetime_old_window_events(self):
        self.run_case("saver_lifetime","old-window-events")

    def test_saver_lifetime_create_failure(self):
        self.run_case("saver_lifetime","create-failure")

    def test_saver_lifetime_create_success(self):
        self.run_case("saver_lifetime","create-success")

    def test_saver_lifetime_free_attr(self):
        self.run_case("saver_lifetime","free-attr")


if __name__ == "__main__":
    unittest.main()
