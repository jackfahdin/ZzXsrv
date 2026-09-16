"""Exercise Fontconfig's actual static library, generated tables and locale path."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from test_freetype import required_file, run_logged

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable local tools after an x64 Release build')
class FontconfigApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('Fontconfig tests require x64 MSVC')
        # A separately built old tree can prove rejection of stale libraries.
        built = Path(os.environ.get('VCXSRV_TEST_FONTCONFIG_ROOT', ROOT))
        cls.temp = tempfile.TemporaryDirectory(prefix='vcxsrv_fontconfig_api_')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.env = dict(os.environ, HOME=str(cls.work),
                       XDG_CACHE_HOME=str(cls.work / 'cache'),
                       FONTCONFIG_FILE=str(cls.work / 'fonts.conf'),
                       FONTCONFIG_PATH=str(cls.work))
        (cls.work / 'fonts.conf').write_text('<fontconfig></fontconfig>', encoding='utf-8')
        libraries = [built / p for p in (
            'third_party/fonts/fontconfig/src/obj64/release/libfontconfig.lib',
            'third_party/fonts/freetype/objs/x64/Release/freetype.lib',
            'third_party/libxml2/build/x64/Release/libxml2.lib',
            'third_party/pthreads/libpthreadVC364.lib')]
        for p in libraries:
            required_file(p)
        for p in ('third_party/fonts/freetype/objs/x64/Release/freetype.dll',
                  'third_party/libxml2/build/x64/Release/libxml2.dll',
                  'third_party/libiconv/build/x64/Release/libiconv.dll',
                  'third_party/zlib/obj64/release/zlib1.dll'):
            shutil.copy2(required_file(built / p), cls.work)
        cls.exe = cls.work / 'fontconfig_api.exe'
        run_logged([compiler, '/nologo', '/std:c11', '/W4', '/WX', '/MD',
                    '/I' + str(built / 'third_party/fonts/fontconfig'),
                    ROOT / 'tools/tests/native/fontconfig_api.c', *libraries,
                    'advapi32.lib', 'user32.lib', 'ws2_32.lib', 'shell32.lib',
                    '/Fe:' + str(cls.exe)], cwd=cls.work, timeout=120)

    def check_api(self, mode):
        self.assertIn('PASS ' + mode,
                      run_logged([self.exe, mode], cwd=self.work, env=self.env))

    def test_runtime_version(self):
        self.check_api('version')

    def test_decimal_in_non_c_locale(self):
        self.check_api('decimal')

    def test_constant_name_lookup(self):
        self.check_api('constants')

    def test_generic_family_roundtrip(self):
        self.check_api('generic')

    def test_explicit_configuration_defaults(self):
        self.check_api('defaults')


if __name__ == '__main__':
    unittest.main()
