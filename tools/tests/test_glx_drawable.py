"""Compile unmodified GLX request functions with real protocol types and macros.

Only drawable lookup and unrelated vendor services are fixtures. Function bodies
are extracted at build time, so both byte orders exercise the production checks.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def function(source, name):
    start = source.index('\n' + name + '(')
    start = source.rfind('\n', 0, start) + 1
    end = source.index('\n}', start) + 2
    return source[start:end]


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable local tools in an x64 MSVC developer environment')
class GlxDrawableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('cl.exe missing')
        cls.temp = tempfile.TemporaryDirectory(prefix='vcxsrv_glx_drawable_')
        cls.addClassCleanup(cls.temp.cleanup)
        work = Path(cls.temp.name)
        normal = (ROOT / 'src/xorg-server/glx/glxcmds.c').read_text()
        swapped = (ROOT / 'src/xorg-server/glx/glxcmdsswap.c').read_text()
        names = ['ChangeDrawableAttributes', 'GetFBConfigsSGIX', 'DestroyPixmap',
                 'DestroyWindow', 'GetDrawableAttributes']
        bodies = [function(normal, 'DoChangeDrawableAttributes')]
        bodies += [function(normal, '__glXDisp_' + name) for name in names]
        bodies += [function(swapped, '__glXDispSwap_' + name) for name in names]
        template = (ROOT / 'tools/tests/native/glx_drawable.c.in').read_text()
        source = work / 'glx_drawable.c'
        source.write_text(template.replace('@FUNCTIONS@', '\n\n'.join(bodies)))
        includes = ['.', 'include', 'third_party/pthreads',
                    'third_party/graphics/pixman/pixman',
                    'third_party/graphics/mesalib/include', 'include/gl/include',
                    'src/xorg-server', 'src/xorg-server/include', 'src/xorg-server/glx',
                    'src/xorg-server/mi', 'src/xorg-server/render', 'src/xorg-server/Xext',
                    'src/xorg-server/miext/damage']
        defines = ['WIN32', '_WINDOWS', 'WINDOWS', '_MBCS', '__i386__', '__MINGW32__',
                   '_POSIX_', 'X_NOT_POSIX', '_TIMEVAL_DEFINED', 'mode_t=int', '__STDC__',
                   'FAKEIT', 'HAVE_CONFIG_H', '_BSD_SOURCE', '_WIN32_WINNT=0x0601',
                   'XKB_IN_SERVER', 'XFree86Server', 'HAVE_DIX_CONFIG_H', 'PIXMAN_API=']
        cls.exe = work / 'glx_drawable.exe'
        command = [compiler, '/nologo', '/std:c11', '/Od', '/Gy', '/MD', '/Zi',
                   '/fsanitize=address', *['/I' + str(ROOT / p) for p in includes],
                   *['/D' + d for d in defines], str(source), '/Fe:' + str(cls.exe),
                   '/link', '/OPT:REF', '/INCREMENTAL:NO']
        result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                errors='replace', timeout=120)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def run_case(self, case, swapped):
        result = subprocess.run([str(self.exe), case, str(int(swapped))],
                                capture_output=True, text=True, errors='replace', timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS', result.stdout)


def make_test(case, swapped):
    def test(self):
        self.run_case(case, swapped)
    return test


for _case in ['zero', 'valid', 'unknown', 'short-header', 'missing-pair',
              'half-pair', 'extra-data', 'count-overflow', 'largest-count',
              'invalid-drawable', 'fixed-valid', 'fixed-short', 'fixed-extra']:
    for _swapped in (False, True):
        setattr(GlxDrawableTests, 'test_' + _case.replace('-', '_') +
                ('_swapped' if _swapped else ''), make_test(_case, _swapped))
