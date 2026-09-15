"""Exercise shipped R8 components; explicit BUILD_ROOT permits old-product checks.

These catch stale DLL/CLI packaging, lost zlib exports, Windows file modes,
keymap path/argument regressions and public-header/static-library mismatches.
"""
import ctypes as C
import gzip
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(os.environ.get('VCXSRV_TEST_R8_BUILD_ROOT', ROOT))
RUNTIME = Path(os.environ.get('VCXSRV_RUNTIME_DIR', BUILD / 'dist/x64/Release'))
ENABLED = os.environ.get('VCXSRV_TEST_LOCAL_TOOLS')


@unittest.skipUnless(ENABLED, 'enable native build tests')
class ZlibRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dll = C.CDLL(str(RUNTIME / 'zlib1.dll'))

    def test_packaged_version(self):
        self.dll.zlibVersion.restype = C.c_char_p
        self.assertEqual(self.dll.zlibVersion(), b'1.3.2')

    def test_size_t_compression_bound_export(self):
        self.assertTrue(hasattr(self.dll, 'compressBound_z'), 'missing size_t API')
        bound = self.dll.compressBound_z
        bound.argtypes, bound.restype = [C.c_size_t], C.c_size_t
        self.assertGreater(bound(1 << 32), 1 << 32)

    def test_binary_compression_roundtrip(self):
        data = bytes(range(256)) * 40
        packed, restored = C.create_string_buffer(12000), C.create_string_buffer(len(data))
        packed_len, restored_len = C.c_ulong(len(packed)), C.c_ulong(len(restored))
        self.dll.compress2.argtypes = [C.c_void_p, C.POINTER(C.c_ulong), C.c_void_p, C.c_ulong, C.c_int]
        self.dll.uncompress.argtypes = [C.c_void_p, C.POINTER(C.c_ulong), C.c_void_p, C.c_ulong]
        self.assertEqual(self.dll.compress2(packed, C.byref(packed_len), data, len(data), 6), 0)
        self.assertEqual(self.dll.uncompress(restored, C.byref(restored_len), packed, packed_len.value), 0)
        self.assertEqual(restored_len.value, len(data))
        self.assertEqual(restored.raw, data)

    def test_crc_known_vector(self):
        self.dll.crc32.argtypes = [C.c_ulong, C.c_void_p, C.c_uint]
        self.dll.crc32.restype = C.c_ulong
        self.assertEqual(self.dll.crc32(0, b'123456789', 9), 0xcbf43926)

    def test_gzip_file_modes_and_independent_reader(self):
        self.dll.gzopen.argtypes, self.dll.gzopen.restype = [C.c_char_p, C.c_char_p], C.c_void_p
        self.dll.gzwrite.argtypes = [C.c_void_p, C.c_void_p, C.c_uint]
        self.dll.gzread.argtypes = [C.c_void_p, C.c_void_p, C.c_uint]
        self.dll.gzclose.argtypes = [C.c_void_p]
        with tempfile.TemporaryDirectory(prefix='r8 gzip ') as directory:
            path = Path(directory) / 'normal.gz'
            payload = bytes(range(256)) * 20
            for mode, data in [(b'wb', payload), (b'ab', b' world')]:
                stream = self.dll.gzopen(os.fsencode(path), mode)
                self.assertTrue(stream)
                try:
                    self.assertEqual(self.dll.gzwrite(stream, data, len(data)), len(data))
                finally:
                    self.assertEqual(self.dll.gzclose(stream), 0)
            exclusive = self.dll.gzopen(os.fsencode(path), b'wbx')
            if exclusive:
                self.dll.gzclose(exclusive)
            self.assertIsNone(exclusive)
            expected = payload + b' world'
            self.assertEqual(gzip.decompress(path.read_bytes()), expected)
            stream = self.dll.gzopen(os.fsencode(path), b'rb')
            self.assertTrue(stream)
            try:
                restored = C.create_string_buffer(len(expected) + 1)
                self.assertEqual(self.dll.gzread(stream, restored, len(restored)), len(expected))
                self.assertEqual(restored.raw[:len(expected)], expected)
            finally:
                self.assertEqual(self.dll.gzclose(stream), 0)


@unittest.skipUnless(ENABLED, 'enable native build tests')
class XkbcompRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='r8 keyboard with spaces ')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.exe = RUNTIME / 'xkbcomp.exe'

    def run_xkb(self, *args):
        result = subprocess.run([str(self.exe), *map(str, args)], cwd=self.work,
                                capture_output=True, text=True, errors='replace', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_version_and_long_option(self):
        for option in ['-version', '--version']:
            with self.subTest(option=option):
                self.assertIn('xkbcomp 1.5.0', self.run_xkb(option))

    def test_help_alias(self):
        self.assertIn('Usage:', self.run_xkb('--help'))

    def compile_and_roundtrip(self, symbols, warning):
        source = self.work / 'input keymap.xkb'
        source.write_text('xkb_keymap {\n'
                          'xkb_keycodes { include "evdev+aliases(qwerty)" };\n'
                          'xkb_types { include "complete" };\n'
                          'xkb_compatibility { include "complete" };\n'
                          f'xkb_symbols {{ include "{symbols}" }};\n'
                          '};\n', encoding='ascii')
        binary = self.work / 'compiled keymap.xkm'
        text = self.work / 'resolved keymap.xkb'
        self.run_xkb('-w' + str(warning), '-R' + str(RUNTIME / 'xkbdata'), '-xkm', source, binary)
        self.assertGreater(binary.stat().st_size, 100)
        self.run_xkb('-xkb', binary, text)
        resolved = text.read_text()
        self.assertIn('<AC01>', resolved)
        self.assertIn('Shift_L', resolved)
        self.run_xkb('-xkm', text, self.work / 'roundtrip.xkm')
        final = self.work / 'roundtrip.xkb'
        self.run_xkb('-xkb', self.work / 'roundtrip.xkm', final)
        return final.read_text()

    def test_us_keymap_external_root_and_quoted_paths(self):
        for warning in [0, 1]:
            with self.subTest(warning=warning):
                text = self.compile_and_roundtrip('pc+us+inet(evdev)', warning)
                self.assertIsNotNone(re.search(r'(?s)key\s+<AD01>\s*\{[^}]*\bq\s*,\s*Q', text),
                                     'US AD01 must retain q/Q after binary roundtrip')

    def test_two_groups_survive_roundtrip(self):
        text = self.compile_and_roundtrip('pc+us+de:2+inet(evdev)+group(alt_shift_toggle)', 1)
        self.assertIn('Group2', text)
        self.assertTrue('odiaeresis' in text, 'German umlaut must survive binary roundtrip')


@unittest.skipUnless(ENABLED, 'enable native build tests')
class XpmConsumerTests(unittest.TestCase):
    def test_public_header_and_production_static_library(self):
        self.assertIsNotNone(shutil.which('cl.exe'), 'x64 MSVC environment required')
        with tempfile.TemporaryDirectory(prefix='r8 xpm ') as directory:
            work = Path(directory)
            exe = work / 'xpm_consumer.exe'
            for dll in RUNTIME.glob('*.dll'):
                shutil.copy2(dll, work)
            command = [shutil.which('cl.exe'), '/nologo', '/W4', '/WX', '/MD',
                       '/D_CRT_SECURE_NO_WARNINGS', '/DWIN32', '/I' + str(BUILD / 'include'),
                       ROOT / 'tools/tests/native/xpm_consumer.c',
                       BUILD / 'third_party/xorg/libXpm/src/obj64/release/libXpm.lib',
                       BUILD / 'third_party/xorg/libX11/obj64/release/libX11.lib',
                       '/Fe:' + str(exe)]
            result = subprocess.run(list(map(str, command)), cwd=work, capture_output=True,
                                    text=True, errors='replace', timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run([str(exe)], cwd=work, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), 'XPM pixels and file roundtrip PASS')
