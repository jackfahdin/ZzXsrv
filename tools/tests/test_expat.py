"""Expat release identity, imported bytes, and real static-library parsing.

Enable native checks with VCXSRV_TEST_LOCAL_TOOLS=1 after an x64 Release build.
The optional VCXSRV_TEST_EXPAT_LIBRARY override is for old-library comparisons.
"""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPAT = ROOT / 'third_party/expat'


class ExpatSourceTests(unittest.TestCase):
    def test_release_identity(self):
        header = (EXPAT / 'lib/expat.h').read_text(encoding='utf-8')
        for name, value in [('MAJOR', 2), ('MINOR', 8), ('MICRO', 4)]:
            match = re.search(rf'#\s*define XML_{name}_VERSION\s+(\d+)\b', header)
            self.assertIsNotNone(match, name)
            self.assertEqual(int(match[1]), value, name)

    def test_official_source_bytes(self):
        manifest = json.loads((EXPAT / 'source-files.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['archive_sha256'],
                         '656ae1cc8da3b4ea513bb4e254f33e6243938084c0ec6239da873376b09985a7')
        for name, digest in manifest['files'].items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((EXPAT / name).read_bytes()).hexdigest(), digest)


@unittest.skipUnless(os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'), 'enable native build tests')
class ExpatApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt' or not shutil.which('cl.exe'):
            raise RuntimeError('Expat tests need x64 MSVC')
        cls.temp = tempfile.TemporaryDirectory(prefix='zzxsrv_expat_')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'expat_api.exe'
        library = Path(os.environ.get('VCXSRV_TEST_EXPAT_LIBRARY',
                                      EXPAT / 'lib/obj64/release/libexpat.lib'))
        if not library.is_file():
            raise RuntimeError(f'Missing production library: {library}')
        cls.run_command([shutil.which('cl.exe'), '/nologo', '/std:c11', '/W4', '/WX', '/MD',
                         '/DXML_STATIC', '/I' + str(EXPAT / 'lib'),
                         ROOT / 'tools/tests/native/expat_api.c', library,
                         '/Fe:' + str(cls.exe)])

    @classmethod
    def run_command(cls, command):
        result = subprocess.run([str(x) for x in command], cwd=cls.work,
                                capture_output=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout

    def parse(self, data, mode='parse'):
        path = self.work / 'fixture.xml'
        path.write_bytes(data)
        return self.run_command([self.exe, mode, path])

    def test_runtime_version(self):
        self.assertIn('VERSION 2.8.4\n', self.run_command([self.exe, 'version']))

    def test_features_preserve_narrow_character_dtd_and_namespaces(self):
        output = self.run_command([self.exe, 'version'])
        self.assertIn('CHAR 1\n', output)
        for line in ['FEATURE 3 0', 'FEATURE 4 1024', 'FEATURE 8 0']:
            self.assertIn(line + '\n', output)

    def test_chunked_utf8(self):
        self.assertIn('RESULT 2 中文𠀀\n', self.parse('<r><v>中文𠀀</v></r>'.encode()))

    def test_chunked_utf16(self):
        self.assertIn('RESULT 2 中文𠀀\n', self.parse('<r><v>中文𠀀</v></r>'.encode('utf-16')))

    def test_namespaces(self):
        output = self.parse(b'<r xmlns="urn:zzxsrv"><v>ok</v></r>', 'namespace')
        self.assertIn('ELEMENT urn:zzxsrv|v\n', output)
        self.assertIn('RESULT 2 ok\n', output)

    def test_small_internal_entity(self):
        output = self.parse(b'<!DOCTYPE r [<!ENTITY greeting "hello">]><r>&greeting;</r>')
        self.assertIn('RESULT 1 hello\n', output)

    def test_parser_reset(self):
        output = self.parse(b'<r>again</r>', 'reset')
        self.assertEqual(output.count('RESULT 1 again\n'), 2)


if __name__ == '__main__':
    unittest.main()
