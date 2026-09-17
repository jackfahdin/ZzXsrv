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

    def test_zip_mirrors_dist_tree(self):
        zip_path = self.out / "zzxsrv-1.0.0-x64-portable.zip"
        count = self.module.make_zip(self.dist, zip_path)
        self.assertEqual(count, 3)
        with zipfile.ZipFile(zip_path) as zf:
            self.assertIsNone(zf.testzip())
            names = zf.namelist()
        self.assertEqual(
            sorted(names),
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


if __name__ == "__main__":
    unittest.main()
