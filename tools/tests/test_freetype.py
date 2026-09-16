"""Public API and real font consumers against the built x64 FreeType 2.14.3 DLL.

Enable with VCXSRV_TEST_LOCAL_TOOLS=1 in an x64 MSVC environment after building.
Missing build outputs are errors once enabled. Fixtures are the repository's
licensed Vera font, public-domain BDF fonts, and an original generated CFF OTF.
"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import struct
import tempfile
import unittest
from xml.sax.saxutils import escape

from native.freetype_fixtures import make_cff_font

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / 'src/xorg-server/fonts.src'
FREETYPE = ROOT / 'third_party/fonts/freetype'
LOCAL_TOOLS = bool(os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'))


def required_file(path):
    if not path.is_file():
        raise RuntimeError(f'Required local build output or fixture missing: {path}')
    return path


def run_logged(command, cwd=None, env=None, timeout=60):
    result = subprocess.run([str(p) for p in command], cwd=cwd, env=env,
                            capture_output=True, text=True, errors='replace', timeout=timeout)
    print('RUN ' + subprocess.list2cmdline([str(p) for p in command]), flush=True)
    print(result.stdout + result.stderr, flush=True)
    if result.returncode:
        raise AssertionError(f'Exit {result.returncode}: {result.stdout}{result.stderr}')
    return result.stdout


@unittest.skipUnless(LOCAL_TOOLS, 'enable local tools in an x64 MSVC developer environment')
class FreeTypeApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt' or not shutil.which('cl.exe'):
            raise RuntimeError('FreeType local tests require Windows and x64 MSVC cl.exe')
        # An override permits an isolated old-release build to prove the runtime
        # version check rejects a stale DLL. Ordinary runs use production output.
        built = Path(os.environ.get('VCXSRV_TEST_FREETYPE_DIR',
                                   str(FREETYPE / 'objs/x64/Release')))
        library = required_file(built / 'freetype.lib')
        dll = required_file(built / 'freetype.dll')
        cls.temp = tempfile.TemporaryDirectory(prefix='vcxsrv_freetype_')
        cls.addClassCleanup(cls.temp.cleanup)
        work = Path(cls.temp.name)
        shutil.copy2(dll, work / 'freetype.dll')
        print(f'DLL {dll} SHA256 {hashlib.sha256(dll.read_bytes()).hexdigest()}', flush=True)
        cls.exe = work / 'freetype_api.exe'
        run_logged([shutil.which('cl.exe'), '/nologo', '/std:c11', '/W4', '/WX', '/MD',
                    '/D_CRT_SECURE_NO_WARNINGS', '/I' + str(FREETYPE / 'include'),
                    ROOT / 'tools/tests/native/freetype_api.c', library,
                    '/Fe:' + str(cls.exe)], cwd=work, timeout=120)
        cls.otf = work / 'rectangle.otf'
        cls.otf.write_bytes(make_cff_font())

    def render(self, font, codepoint, driver, mode='gray', presence='present'):
        output = run_logged([self.exe, required_file(font), codepoint, driver, mode, presence])
        self.assertIn('PASS render', output)

    def test_runtime_version(self):
        self.assertIn('PASS version', run_logged([self.exe, 'version']))

    def test_ttf_grayscale(self):
        self.render(FONTS / 'TTF/Vera.ttf', '41', 'TrueType')

    def test_ttf_monochrome(self):
        self.render(FONTS / 'TTF/Vera.ttf', '41', 'TrueType', 'mono')

    def test_otf_cff_grayscale(self):
        self.render(self.otf, '41', 'CFF')

    def test_otf_cff_monochrome(self):
        self.render(self.otf, '41', 'CFF', 'mono')

    def test_missing_character_uses_notdef(self):
        self.render(FONTS / 'TTF/Vera.ttf', '10FFFF', 'TrueType', presence='missing')

    def test_bdf_latin_bitmap(self):
        self.render(FONTS / 'misc/6x13.bdf', '41', 'BDF', 'mono')

    def test_bdf_cjk_bitmap(self):
        self.render(FONTS / 'misc/18x18ja.bdf', '4E2D', 'BDF', 'mono')


@unittest.skipUnless(LOCAL_TOOLS, 'enable local tools after an x64 Release build')
class FreeTypeConsumerTests(unittest.TestCase):
    def setUp(self):
        if os.name != 'nt' or not shutil.which('cl.exe'):
            raise RuntimeError('FreeType consumers require Windows and x64 MSVC cl.exe')
        self.temp = tempfile.TemporaryDirectory(prefix='vcxsrv_freetype_consumer_')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.fontdir = self.work / 'fonts'
        self.fontdir.mkdir()
        shutil.copy2(required_file(FONTS / 'TTF/Vera.ttf'), self.fontdir)
        shutil.copy2(required_file(FONTS / 'TTF/COPYRIGHT.TXT'), self.fontdir)
        (self.fontdir / 'rectangle.otf').write_bytes(make_cff_font())
        # Keep all writable configuration and caches under the temporary root.
        self.env = dict(os.environ, HOME=str(self.work), XDG_CACHE_HOME=str(self.work / 'xdg'))

    def test_fontconfig_cache_reload_list_and_match(self):
        cache = self.work / 'cache'
        cache.mkdir()
        config = self.work / 'fonts.conf'
        config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">'
                          '<fontconfig><dir>' + escape(self.fontdir.as_posix()) + '</dir>'
                          '<cachedir>' + escape(cache.as_posix()) + '</cachedir></fontconfig>',
                          encoding='utf-8')
        self.env.update(FONTCONFIG_FILE=str(config), FONTCONFIG_PATH=str(self.work))
        libraries = [
            ROOT / 'third_party/fonts/fontconfig/src/obj64/release/libfontconfig.lib',
            FREETYPE / 'objs/x64/Release/freetype.lib',
            ROOT / 'third_party/libxml2/build/x64/Release/libxml2.lib',
            ROOT / 'third_party/pthreads/libpthreadVC364.lib',
        ]
        for library in libraries:
            required_file(library)
        shutil.copy2(required_file(FREETYPE / 'objs/x64/Release/freetype.dll'), self.work)
        shutil.copy2(required_file(ROOT / 'third_party/libxml2/build/x64/Release/libxml2.dll'), self.work)
        shutil.copy2(required_file(ROOT / 'third_party/libiconv/build/x64/Release/libiconv.dll'), self.work)
        shutil.copy2(required_file(ROOT / 'third_party/zlib/obj64/release/zlib1.dll'), self.work)
        exe = self.work / 'freetype_fontconfig.exe'
        run_logged([shutil.which('cl.exe'), '/nologo', '/std:c11', '/W4', '/WX', '/MD',
                    '/I' + str(FREETYPE / 'include'),
                    '/I' + str(ROOT / 'third_party/fonts/fontconfig'),
                    ROOT / 'tools/tests/native/freetype_fontconfig.c', *libraries,
                    'advapi32.lib', 'user32.lib', 'ws2_32.lib', 'shell32.lib',
                    '/Fe:' + str(exe)], cwd=self.work, timeout=120)
        self.assertIn('PASS fontconfig build',
                      run_logged([exe, config, self.fontdir, 'build'], cwd=self.work, env=self.env))
        caches = list(cache.glob('*.cache-12'))
        self.assertEqual(len(caches), 1, 'Fontconfig must write the new cache format')
        cache_bytes = caches[0].read_bytes()
        self.assertEqual(struct.unpack_from('<i', cache_bytes, 4)[0], 12)
        self.assertEqual(struct.unpack_from('<q', cache_bytes, 64)[0],
                         (2 << 24) + (18 << 12) + 3)
        # A second process must load the disk cache; it cannot use in-memory state.
        self.assertIn('PASS fontconfig reload',
                      run_logged([exe, config, self.fontdir, 'reload'], cwd=self.work, env=self.env))
        self.assertEqual(caches[0].read_bytes(), cache_bytes,
                         'Reload must consume the existing cache without rewriting it')

    def test_mkfontscale_indexes_ttf_and_cff(self):
        exe = required_file(ROOT / 'third_party/xorg/mkfontscale/obj64/release/mkfontscale.exe')
        # Copy the production tool with its adjacent runtime dependencies. This
        # also prevents a stale PATH DLL from changing the FreeType under test.
        shutil.copy2(exe, self.work)
        for dll in exe.parent.glob('*.dll'):
            shutil.copy2(dll, self.work)
        shutil.copy2(required_file(FREETYPE / 'objs/x64/Release/freetype.dll'), self.work)
        run_logged([self.work / exe.name, self.fontdir], cwd=self.work, env=self.env)
        lines = required_file(self.fontdir / 'fonts.scale').read_text().splitlines()
        self.assertEqual(int(lines[0]), len(lines) - 1)
        self.assertGreater(len(lines), 2)
        entries = {line.split(' ', 1)[0] for line in lines[1:]}
        self.assertEqual(entries, {'Vera.ttf', 'rectangle.otf'})


if __name__ == '__main__':
    unittest.main()
