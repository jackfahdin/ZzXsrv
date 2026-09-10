"""Run the native XKB data installer against the checked-in generators."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "tools" / "build_xkbdata.py"
SOURCE = ROOT / "src" / "xorg-server" / "xkeyboard-config"


class BuildXkbdataTests(unittest.TestCase):
    def invoke(self, output, *arguments):
        return subprocess.run(
            [sys.executable, str(HELPER), "--output", str(output), *map(str, arguments)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_installs_rules_data_and_generated_compatibility_symbols(self):
        # Wrong part order/numbering or skipped generators lose actual aliases.
        original_fi = (SOURCE / "symbols" / "fi").read_bytes()
        with tempfile.TemporaryDirectory(prefix="xkb data test ") as temporary:
            output = Path(temporary) / "installed"
            result = self.invoke(output, "--source", SOURCE)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertTrue((output / ".native-build.stamp").is_file())
            for filename in ("compat/complete", "geometry/pc", "keycodes/evdev", "types/complete", "symbols/us", "symbols/xfree68_vndr/amiga", "rules/README", "rules/xkb.dtd", "rules/xfree98"):
                self.assertEqual((output / filename).read_bytes(), (SOURCE / filename).read_bytes())
            for ruleset in ("base", "evdev"):
                rules = (output / "rules" / ruleset).read_text(encoding="utf-8")
                self.assertIn("! model", rules)
                self.assertIn("ben", rules)
                self.assertIn("in(ben)", rules)
                self.assertIn("caps:escape", rules)
                self.assertIn("+capslock(escape)", rules)
                self.assertEqual((output / "rules" / (ruleset + ".xml")).read_bytes(), (SOURCE / "rules" / "base.xml").read_bytes())
                self.assertEqual((output / "rules" / (ruleset + ".extras.xml")).read_bytes(), (SOURCE / "rules" / "base.extras.xml").read_bytes())
                listing = (output / "rules" / (ruleset + ".lst")).read_text(encoding="utf-8")
                for section in ("! model", "! layout", "! variant", "! option"):
                    self.assertIn(section, listing)
                self.assertIn("English (US)", listing)
            for suffix in ("", ".xml", ".lst"):
                self.assertEqual((output / "rules" / ("xorg" + suffix)).read_bytes(), (output / "rules" / ("base" + suffix)).read_bytes())
            fi = (output / "symbols" / "fi").read_text(encoding="utf-8")
            self.assertIn('xkb_symbols "basic"', fi)
            self.assertIn('include "fi(classic)"', fi)
            self.assertEqual((SOURCE / "symbols" / "fi").read_bytes(), original_fi)
            self.assertFalse((output / "symbols" / "caps").exists())
            self.assertFalse((output / "types" / "custom").exists())
            for path in output.rglob("*"):
                self.assertNotIn(path.name.lower(), ("makefile", "meson.build", "__pycache__"))
                self.assertNotIn(path.suffix.lower(), (".mk", ".py", ".pyc"))

    def test_missing_source_fails_without_creating_destination(self):
        # A missing checkout must not silently produce a partial data tree.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            result = self.invoke(output, "--source", Path(temporary) / "missing")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"error:", result.stderr.lower())
            self.assertFalse(output.exists())

    def test_source_destination_overlap_is_rejected(self):
        # Never overwrite source files, including through a nested output path.
        result = self.invoke(SOURCE / "forbidden-output", "--source", SOURCE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"overlap", result.stderr.lower())
        self.assertFalse((SOURCE / "forbidden-output").exists())


if __name__ == "__main__":
    unittest.main()
