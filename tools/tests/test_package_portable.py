"""Runtime staging must validate inputs before publishing a runnable folder."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "package_portable.py"


class PortablePackageTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("package_portable", HELPER)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temporary = tempfile.TemporaryDirectory(prefix="vcxsrv portable ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.installer = self.root / "installer"
        self.installer.mkdir()
        self.crt = self.root / "CRT"
        self.crt.mkdir()
        self.output = self.root / "output"
        (self.root / "vcxsrv.exe").write_bytes(b"server")
        (self.crt / "vcruntime140.dll").write_bytes(b"runtime")
        (self.root / "fonts").mkdir()
        (self.root / "fonts" / "fonts.dir").write_text("1\n")
        self.manifest = self.installer / "vcxsrv.nsi"
        self.manifest.write_text('''Section "VcXsrv (required)"
SetOutPath $INSTDIR
File "..\\vcxsrv.exe"
File "vcruntime140.dll"
SectionEnd
Section "Fonts"
SetOutPath $INSTDIR\\fonts
File /r "..\\fonts\\*.*"
SectionEnd
Section "Start Menu Shortcuts"
File "must-not-be-read.exe"
SectionEnd
''')

    def test_copies_runtime_and_data_without_executing_installer_actions(self):
        self.module.package(self.manifest, self.crt, self.output)
        self.assertEqual((self.output / "vcxsrv.exe").read_bytes(), b"server")
        self.assertEqual((self.output / "vcruntime140.dll").read_bytes(), b"runtime")
        self.assertEqual((self.output / "fonts" / "fonts.dir").read_text(), "1\n")

    def test_missing_runtime_does_not_publish_partial_output(self):
        (self.crt / "vcruntime140.dll").unlink()
        with self.assertRaises(FileNotFoundError):
            self.module.package(self.manifest, self.crt, self.output)
        self.assertFalse(self.output.exists())

    def test_output_cannot_overwrite_source_tree(self):
        with self.assertRaises(ValueError):
            self.module.package(self.manifest, self.crt, self.root)
        self.assertEqual((self.root / "vcxsrv.exe").read_bytes(), b"server")


if __name__ == "__main__":
    unittest.main()
