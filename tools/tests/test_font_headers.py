"""Keep the public copies used first by mhmake aligned with this import."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class FontHeaderTests(unittest.TestCase):
    def test_updated_shared_headers_match_component(self):
        # The global include directory precedes the component include directory.
        # Comparing both copies prevents a correct vendored header being shadowed.
        for name in ('bdfint.h', 'libxfont2.h'):
            with self.subTest(header=name):
                shared = ROOT / 'include/X11/fonts' / name
                component = ROOT / 'third_party/xorg/libXfont2/include/X11/fonts' / name
                self.assertEqual(shared.read_text(), component.read_text())


if __name__ == '__main__':
    unittest.main()
