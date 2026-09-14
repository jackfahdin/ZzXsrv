"""Compile real font consumers with MSVC ASan; bounded FPE/render fixtures only."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable local tools in an x64 MSVC developer environment')
class FontConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('cl.exe missing: use an x64 MSVC developer environment')
        cls.temp = tempfile.TemporaryDirectory(prefix='vcxsrv_font_')
        cls.addClassCleanup(cls.temp.cleanup)
        work = Path(cls.temp.name)
        # Extract complete function bodies verbatim, never reproduce their logic.
        source = (ROOT / 'src/xorg-server/dix/dixfonts.c').read_text()
        pieces = []
        for start, end in [('static int\nFontToXError(', 'static int\nLoadGlyphs('),
                           ('static Bool\ndoListFontsAndAliases(', 'int\nListFonts('),
                           ('static int\ndoListFontsWithInfo(', 'int\nStartListFontsWithInfo(')]:
            first = source.index(start)
            pieces.append(source[first:source.index(end, first)])
        template = (ROOT / 'tools/tests/native/font_consumer_alias.c.in').read_text()
        cfile = work / 'font_consumer_alias.c'
        cfile.write_text(template.replace('@FUNCTIONS@', '\n'.join(pieces)))
        includes = ['.', 'include', 'third_party/pthreads', 'third_party/graphics/pixman/pixman',
                    'third_party/graphics/mesalib/include', 'include/gl/include',
                    'src/xorg-server', 'src/xorg-server/include', 'src/xorg-server/dix',
                    'src/xorg-server/mi', 'src/xorg-server/fb', 'src/xorg-server/render',
                    'src/xorg-server/Xext', 'src/xorg-server/miext/damage', 'src/xorg-server/present']
        defines = ['WIN32', '_WINDOWS', 'WINDOWS', '_MBCS', '__i386__', '__MINGW32__',
                   '_POSIX_', 'X_NOT_POSIX', '_TIMEVAL_DEFINED', 'mode_t=int', '__STDC__',
                   'FAKEIT', 'HAVE_CONFIG_H', '_BSD_SOURCE', '_WIN32_WINNT=0x0601',
                   'XKB_IN_SERVER', 'XFree86Server', 'HAVE_DIX_CONFIG_H', 'PIXMAN_API=']
        cls.executables = {}
        for kind, path in [('alias', cfile), ('glyph', ROOT / 'tools/tests/native/font_consumer_glyph.c')]:
            exe = work / ('font_consumer_' + kind + '.exe')
            command = [compiler, '/nologo', '/std:c11', '/Od', '/Gy', '/Gw', '/Zc:inline', '/MD', '/Zi',
                       '/fsanitize=address', *['/I' + str(ROOT / p) for p in includes],
                       *['/D' + d for d in defines], str(path), '/Fe:' + str(exe),
                       '/link', '/OPT:REF', '/INCREMENTAL:NO']
            result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                    errors='replace', timeout=120)
            print('COMPILE ' + subprocess.list2cmdline(command), flush=True)
            print(result.stdout + result.stderr, flush=True)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            cls.executables[kind] = exe

    def run_case(self, kind, *args):
        result = subprocess.run([str(self.executables[kind]), *args], capture_output=True,
                                text=True, errors='replace', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS ' + ' '.join(args), result.stdout)


def alias_case(mode, case):
    return lambda self: self.run_case('alias', mode, case)


for mode in ('list', 'info'):
    for case in ('normal', 'edge', 'overlong', 'oom', 'start-error', 'suspend', 'client-gone'):
        setattr(FontConsumerTests, 'test_' + mode + '_' + case.replace('-', '_'), alias_case(mode, case))
for case in ('missing-name', 'missing-start-name', 'missing-length'):
    setattr(FontConsumerTests, 'test_info_' + case.replace('-', '_'), alias_case('info', case))
setattr(FontConsumerTests, 'test_list_missing_length', alias_case('list', 'missing-length'))
for mode in ('fb-poly', 'fb-image', 'mi-poly'):
    for case in ('negative-width', 'negative-height', 'zero-width', 'zero-height', 'positive'):
        def glyph_case(self, mode=mode, case=case):
            self.run_case('glyph', mode, case)
        setattr(FontConsumerTests, 'test_' + mode.replace('-', '_') + '_' + case.replace('-', '_'), glyph_case)

if __name__ == '__main__':
    unittest.main()

