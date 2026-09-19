"""Release packaging must produce a portable zip that faithfully mirrors the dist tree."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile


HELPER = Path(__file__).resolve().parents[1] / "package_release.py"


class ReleasePackageTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("package_release", HELPER)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temporary = tempfile.TemporaryDirectory(prefix="zzxsrv release ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.dist = self.root / "dist"
        (self.dist / "fonts" / "misc").mkdir(parents=True)
        (self.dist / "vcxsrv.exe").write_bytes(b"server")
        (self.dist / "libX11.dll").write_bytes(b"lib")
        (self.dist / "fonts" / "misc" / "fonts.dir").write_text("1\n")
        self.out = self.root / "out"
        self.out.mkdir()

    def populate_slim_targets(self):
        for rel in self.module.SLIM_EXCLUDES:
            (self.dist / rel).write_bytes(b"excluded")

    def zip_names(self, zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            self.assertIsNone(zf.testzip())
            return zf.namelist()

    def test_zip_mirrors_dist_tree(self):
        zip_path = self.out / "zzxsrv-1.0.0-x64-portable.zip"
        count = self.module.make_zip(self.dist, zip_path)
        self.assertEqual(count, 3)
        self.assertEqual(
            sorted(self.zip_names(zip_path)),
            [
                "zzxsrv-1.0.0-x64-portable/fonts/misc/fonts.dir",
                "zzxsrv-1.0.0-x64-portable/libX11.dll",
                "zzxsrv-1.0.0-x64-portable/vcxsrv.exe",
            ],
        )

    def test_missing_dist_is_rejected(self):
        argv = ["package_release.py", "--dist-dir", str(self.root / "nope"), "--zip-only"]
        with unittest.mock.patch("sys.argv", argv):
            self.assertEqual(self.module.main(), 1)

    def test_slim_zip_drops_exclusion_list(self):
        self.populate_slim_targets()
        excludes, warnings = self.module.slim_exclusions(self.dist)
        self.assertEqual(warnings, [])
        self.assertEqual(set(self.module.SLIM_EXCLUDES), excludes)
        zip_path = self.out / "zzxsrv-1.0.0-x64-slim-portable.zip"
        count = self.module.make_zip(self.dist, zip_path, excludes)
        self.assertEqual(count, 3)
        names = self.zip_names(zip_path)
        for rel in self.module.SLIM_EXCLUDES:
            self.assertNotIn(f"zzxsrv-1.0.0-x64-slim-portable/{rel}", names)
        # Fonts and the server itself survive the slim filter.
        self.assertIn("zzxsrv-1.0.0-x64-slim-portable/fonts/misc/fonts.dir", names)
        self.assertIn("zzxsrv-1.0.0-x64-slim-portable/vcxsrv.exe", names)

    def test_full_zip_is_unaffected_by_slim_list(self):
        self.populate_slim_targets()
        zip_path = self.out / "zzxsrv-1.0.0-x64-portable.zip"
        count = self.module.make_zip(self.dist, zip_path)
        self.assertEqual(count, 3 + len(self.module.SLIM_EXCLUDES))
        names = self.zip_names(zip_path)
        for rel in self.module.SLIM_EXCLUDES:
            self.assertIn(f"zzxsrv-1.0.0-x64-portable/{rel}", names)

    def test_missing_exclusion_target_warns(self):
        # Only some targets exist: the rest must produce warnings, not silence.
        (self.dist / "plink.exe").write_bytes(b"ssh")
        excludes, warnings = self.module.slim_exclusions(self.dist)
        self.assertEqual(excludes, {"plink.exe"})
        self.assertEqual(len(warnings), len(self.module.SLIM_EXCLUDES) - 1)
        self.assertTrue(all(w.startswith("warning:") for w in warnings))
        self.assertTrue(any("xlaunch.exe" in w for w in warnings))

    def test_slim_cli_uses_slim_artifact_names(self):
        self.populate_slim_targets()
        argv = ["package_release.py", "--dist-dir", str(self.dist), "--version", "1.0.0",
                "--edition", "slim", "--output-dir", str(self.out), "--zip-only"]
        with unittest.mock.patch("sys.argv", argv):
            self.assertEqual(self.module.main(), 0)
        self.assertTrue((self.out / "zzxsrv-1.0.0-x64-slim-portable.zip").is_file())

    def test_artifact_stem(self):
        self.assertEqual(self.module.artifact_stem("1.0.0", "full"), "zzxsrv-1.0.0-x64")
        self.assertEqual(self.module.artifact_stem("1.0.0", "slim"), "zzxsrv-1.0.0-x64-slim")

    def write_rc(self, version=None):
        rc = self.root / "XWin.rc"
        if version is None:
            rc.write_text("#define VER_PRODUCTVERSION_STR      \"1.0.0.0\"\n")
        else:
            rc.write_text(f'#define VER_FILEVERSION_STR         "{version}"\n')
        return rc

    def test_rc_version_parses_four_part_version(self):
        rc = self.write_rc("21.1.16.1")
        self.assertEqual(self.module.rc_version(rc), "21.1.16.1")

    def test_rc_version_rejects_malformed_value(self):
        with self.assertRaisesRegex(ValueError, "VER_FILEVERSION_STR"):
            self.module.rc_version(self.write_rc("not-a-version"))
        with self.assertRaisesRegex(ValueError, "VER_FILEVERSION_STR"):
            self.module.rc_version(self.write_rc("21.1"))
        with self.assertRaisesRegex(ValueError, "VER_FILEVERSION_STR"):
            self.module.rc_version(self.write_rc("21.1.16.1.2"))

    def test_rc_version_missing_file_or_define(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            self.module.rc_version(self.root / "absent.rc")
        rc = self.write_rc()  # no VER_FILEVERSION_STR at all
        with self.assertRaisesRegex(ValueError, "VER_FILEVERSION_STR"):
            self.module.rc_version(rc)

    def test_rc_version_matches_repo_source_of_truth(self):
        # The real XWin.rc in this checkout currently carries 21.1.16.1.
        self.assertEqual(self.module.rc_version(self.module.VERSION_RC), "21.1.16.1")
        self.assertEqual(self.module.default_version(), "21.1.16.1")

    def test_cli_defaults_to_rc_version(self):
        argv = ["package_release.py", "--dist-dir", str(self.dist),
                "--output-dir", str(self.out), "--zip-only"]
        with unittest.mock.patch("sys.argv", argv):
            self.assertEqual(self.module.main(), 0)
        self.assertTrue((self.out / "zzxsrv-21.1.16.1-x64-portable.zip").is_file())

    def test_cli_explicit_version_overrides_rc_default(self):
        argv = ["package_release.py", "--dist-dir", str(self.dist), "--version", "1.20.14.0",
                "--output-dir", str(self.out), "--zip-only"]
        with unittest.mock.patch("sys.argv", argv):
            self.assertEqual(self.module.main(), 0)
        self.assertTrue((self.out / "zzxsrv-1.20.14.0-x64-portable.zip").is_file())

    def test_cli_rejects_invalid_version(self):
        for bad in ("2026.9", "1.2.3.4.5", "21.1.16.1-beta", "v21.1.16.1"):
            argv = ["package_release.py", "--dist-dir", str(self.dist), "--version", bad,
                    "--output-dir", str(self.out), "--zip-only"]
            with unittest.mock.patch("sys.argv", argv):
                self.assertEqual(self.module.main(), 1, bad)
        # Three-part versions remain accepted under the relaxed format check.
        argv = ["package_release.py", "--dist-dir", str(self.dist), "--version", "21.1.16",
                "--output-dir", str(self.out), "--zip-only"]
        with unittest.mock.patch("sys.argv", argv):
            self.assertEqual(self.module.main(), 0)
        self.assertTrue((self.out / "zzxsrv-21.1.16-x64-portable.zip").is_file())

    def test_resolve_inno_precedence(self):
        explicit = self.root / "explicit" / "ISCC.exe"
        self.assertEqual(self.module.resolve_inno(str(explicit)), explicit)
        with mock.patch.dict("os.environ", {"INNO_SETUP_ISCC": r"C:\env\ISCC.exe"}):
            self.assertEqual(self.module.resolve_inno(None), Path(r"C:\env\ISCC.exe"))
        with mock.patch.dict("os.environ", {}, clear=True), \
                mock.patch.object(self.module.shutil, "which", return_value=r"C:\path\ISCC.exe"):
            self.assertEqual(self.module.resolve_inno(None), Path(r"C:\path\ISCC.exe"))
        with mock.patch.dict("os.environ", {}, clear=True), \
                mock.patch.object(self.module.shutil, "which", return_value=None), \
                mock.patch.object(self.module, "FALLBACK_INNO", str(self.root / "missing" / "ISCC.exe")):
            self.assertIsNone(self.module.resolve_inno(None))


if __name__ == "__main__":
    unittest.main()
