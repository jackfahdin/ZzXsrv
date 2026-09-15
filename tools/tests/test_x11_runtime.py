"""Normal public Xlib calls; BUILD_ROOT also supports old-product comparison."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(os.environ.get('VCXSRV_TEST_X11_BUILD_ROOT', ROOT))
RUNTIME = Path(os.environ.get('VCXSRV_RUNTIME_DIR', BUILD / 'dist/x64/Release'))


@unittest.skipUnless(os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'), 'enable native build tests')
class X11ConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('x64 MSVC environment required')
        cls.temp = tempfile.TemporaryDirectory(prefix='r9 x11 consumer ')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'x11_consumer.exe'
        for dll in RUNTIME.glob('*.dll'):
            shutil.copy2(dll, cls.work)
        command = [compiler, '/nologo', '/W4', '/WX', '/MD', '/DWIN32',
                   '/I' + str(BUILD / 'include'), ROOT / 'tools/tests/native/x11_consumer.c',
                   BUILD / 'third_party/xorg/libX11/obj64/release/libX11.lib',
                   '/Fe:' + str(cls.exe)]
        result = subprocess.run(list(map(str, command)), cwd=cls.work, capture_output=True,
                                text=True, errors='replace', timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def call(self, mode):
        result = subprocess.run([str(self.exe), mode], cwd=self.work, capture_output=True,
                                text=True, errors='replace', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), 'X11 consumer PASS')

    def test_caps_lock_canonical_level_and_mask(self):
        self.call('caps')

    def test_shift_canonical_level_and_mask(self):
        self.call('shift')

    def test_default_keypad_levels_and_modifiers(self):
        self.call('keypad')

    def test_virtual_num_lock_mapping(self):
        self.call('virtual')

    def test_unicode_and_named_keysyms(self):
        self.call('keysyms')
