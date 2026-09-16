"""Exercise Fontconfig's actual static library, generated tables and locale path."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from test_freetype import required_file, run_logged
from native.freetype_fixtures import make_cff_font

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
                       XDG_CONFIG_HOME=str(cls.work / 'config'),
                       FONTCONFIG_FILE=str(cls.work / 'fonts.conf'),
                       FONTCONFIG_PATH=str(cls.work))
        (cls.work / 'fonts.conf').write_text('<fontconfig></fontconfig>', encoding='utf-8')
        # Original rectangle outlines with a known family-name lookup key.
        # The name has no "mono" substring: classification must use the table.
        cls.font = cls.work / 'classification.otf'
        cls.font.write_bytes(make_cff_font(family='Consolas'))
        (cls.work / '.fonts.conf').write_text(
            '<fontconfig><match target="pattern"><edit name="family" mode="assign">'
            '<string>Legacy User</string></edit></match></fontconfig>', encoding='utf-8')
        (cls.work / '.fonts.conf.d').mkdir()
        (cls.work / '.fonts.conf.d/10-local.conf').write_text(
            '<fontconfig><match target="pattern"><edit name="size" mode="assign">'
            '<double>29.5</double></edit></match></fontconfig>', encoding='utf-8')
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
                    '/I' + str(built / 'third_party/fonts/freetype/include'),
                    ROOT / 'tools/tests/native/fontconfig_api.c', *libraries,
                    'advapi32.lib', 'user32.lib', 'ws2_32.lib', 'shell32.lib',
                    '/Fe:' + str(cls.exe)], cwd=cls.work, timeout=120)

    def check_api(self, mode, *args):
        self.assertIn('PASS ' + mode,
                      run_logged([self.exe, mode, *args], cwd=self.work, env=self.env))

    def test_runtime_version(self):
        self.check_api('version')

    def test_decimal_in_non_c_locale(self):
        self.check_api('decimal')

    def test_constant_name_lookup(self):
        self.check_api('constants')

    def test_generic_family_roundtrip(self):
        self.check_api('generic')

    def test_known_family_classification(self):
        self.check_api('classification', self.font)

    def test_legacy_user_file_and_directory_includes(self):
        self.check_api('userconfig', ROOT / 'third_party/fonts/fontconfig/conf.d/50-user.conf')

    def test_explicit_configuration_defaults(self):
        self.check_api('defaults')


if __name__ == '__main__':
    unittest.main()
