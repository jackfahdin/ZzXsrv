"""Release identity and source integrity for native XML dependencies."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class XmlSourceTests(unittest.TestCase):
    def test_imported_files_match_recorded_bytes(self):
        for name, count in [('libxml2', 4426), ('libiconv', 1112)]:
            with self.subTest(component=name):
                component = ROOT / 'third_party' / name
                expected = json.loads((component / 'source-files.json').read_text())['files']
                actual = {p.relative_to(component / 'source').as_posix():
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (component / 'source').rglob('*') if p.is_file()}
                self.assertEqual(len(expected), count)
                self.assertEqual(actual, expected)

    def test_public_iconv_header_matches_native_library(self):
        def normalized(path):
            return path.read_bytes().replace(b'\r\n', b'\n')
        self.assertEqual(normalized(ROOT / 'include/iconv.h'),
                         normalized(ROOT / 'third_party/libiconv/source/include/iconv.h'))
        self.assertIn(b'#define _LIBICONV_VERSION 0x0113', normalized(ROOT / 'include/iconv.h'))

    def test_libxml2_release_and_licenses_are_present(self):
        self.assertEqual((ROOT / 'third_party/libxml2/source/VERSION').read_text().strip(), '2.15.4')
        for path in ['third_party/libxml2/source/Copyright',
                     'third_party/libiconv/source/COPYING.LIB',
                     'third_party/libiconv/source/COPYING']:
            with self.subTest(path=path):
                self.assertGreater((ROOT / path).stat().st_size, 500)

    def test_legacy_xml_headers_and_binaries_are_not_available_to_build(self):
        for name in ['include', 'bin', 'bin64', 'lib', 'lib64']:
            with self.subTest(path=name):
                self.assertFalse((ROOT / 'third_party/libxml2' / name).exists(),
                                 'Retired headers/binaries must not shadow native output')


if __name__ == '__main__':
    unittest.main()
