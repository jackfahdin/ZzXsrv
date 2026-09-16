"""Consume the production static library: catch stale headers and lost render paths."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(os.environ.get('VCXSRV_TEST_PIXMAN_BUILD_ROOT', ROOT))


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable x64 MSVC production-library tests')
class PixmanConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='pixman consumer ')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'pixman_consumer.exe'
        component = BUILD / 'third_party/graphics/pixman'
        cls.version = re.search(r"version\s*:\s*'([^']+)'",
                                (component / 'meson.build').read_text()).group(1)
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('x64 MSVC compiler required')
        command = [compiler, '/nologo', '/W4', '/WX', '/MD', '/DPIXMAN_API=',
                   '/I' + str(component / 'pixman'),
                   str(ROOT / 'tools/tests/native/pixman_consumer.c'),
                   str(component / 'pixman/obj64/release/libpixman-1.lib'),
                   'user32.lib', '/Fe:' + str(cls.exe)]
        result = subprocess.run(command, cwd=cls.work, capture_output=True,
                                text=True, errors='replace', timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def run_case(self, mode):
        for disabled in ('', 'sse2 mmx'):
            with self.subTest(disabled=disabled):
                env = os.environ.copy()
                env['PIXMAN_DISABLE'] = disabled
                result = subprocess.run([str(self.exe), mode, self.version],
                                        cwd=self.work, env=env, capture_output=True,
                                        text=True, errors='replace', timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('PASS ' + mode, result.stdout)

    def test_version_matches_source_and_public_header(self): self.run_case('version')
    def test_premultiplied_over_and_row_padding(self): self.run_case('over')
    def test_a8_mask_composition(self): self.run_case('mask')
    def test_negative_source_stride(self): self.run_case('negative-stride')
    def test_nearest_scaled_image(self): self.run_case('transform')
    def test_destination_clip(self): self.run_case('clip')
    def test_integer_region_subtraction(self): self.run_case('region')
    def test_fractional_region_public_api(self): self.run_case('fractional')

    def test_filter_public_api_links_and_renders(self):
        component = BUILD / 'third_party/graphics/pixman'
        exe = self.work / 'pixman_filter_consumer.exe'
        command = [shutil.which('cl.exe'), '/nologo', '/W4', '/WX', '/MD', '/DPIXMAN_API=',
                   '/I' + str(component / 'pixman'),
                   str(ROOT / 'tools/tests/native/pixman_filter_consumer.c'),
                   str(component / 'pixman/obj64/release/libpixman-1.lib'),
                   'user32.lib', '/Fe:' + str(exe)]
        result = subprocess.run(command, cwd=self.work, capture_output=True,
                                text=True, errors='replace', timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = subprocess.run([str(exe)], cwd=self.work, capture_output=True,
                                text=True, errors='replace', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS convolution', result.stdout)
