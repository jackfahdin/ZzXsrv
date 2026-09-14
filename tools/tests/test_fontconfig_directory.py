"""Real Windows directory enumeration: no duplicated names or stale types."""
from collections import Counter
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable local tools in an x64 MSVC environment')
class FontconfigDirectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('x64 MSVC cl.exe is required')
        cls.temp = tempfile.TemporaryDirectory(prefix='fc_directory_build_')
        cls.addClassCleanup(cls.temp.cleanup)
        work = Path(cls.temp.name)
        source_path = Path(os.environ.get('VCXSRV_TEST_FC_SOURCE',
                                         str(ROOT / 'third_party/fonts/fontconfig/src/fccompat.c')))
        source = source_path.read_text(encoding='utf-8')
        print('SOURCE ' + str(source_path), flush=True)
        start = source.index('struct DIR {')
        implementation = source[start:source.index('#endif /* HAVE_DIRENT_H */', start)]
        template = (ROOT / 'tools/tests/native/fontconfig_directory.c.in').read_text()
        cfile = work / 'directory.c'
        cfile.write_text(template.replace('@DIRECTORY_IMPLEMENTATION@', implementation))
        cls.exe = work / 'directory.exe'
        command = [compiler, '/nologo', '/std:c11', '/W4', '/WX', '/MD',
                   '/D_CRT_SECURE_NO_WARNINGS',
                   '/I' + str(ROOT / 'third_party/fonts/fontconfig'),
                   '/I' + str(ROOT / 'third_party/fonts/fontconfig/src'),
                   str(cfile), '/Fe:' + str(cls.exe)]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                errors='replace', timeout=90)
        print('COMPILE ' + subprocess.list2cmdline(command), flush=True)
        print(result.stdout + result.stderr, flush=True)
        if result.returncode:
            raise RuntimeError('Fontconfig directory harness compilation failed')

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix='fc directory ')
        self.addCleanup(self.tempdir.cleanup)
        self.directory = Path(self.tempdir.name)

    def run_directory(self, mode, path):
        result = subprocess.run([str(self.exe), mode, str(path)], capture_output=True,
                                text=True, errors='replace', timeout=15)
        print(result.stdout + result.stderr, flush=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS ' + mode, result.stdout)
        return [line.split('\t', 2)[1:] for line in result.stdout.splitlines()
                if line.startswith('ENTRY\t')]

    def check_entries(self, files=(), directories=()):
        for name in files:
            (self.directory / name).write_text('normal fixture')
        for name in directories:
            (self.directory / name).mkdir()
        entries = self.run_directory('list', self.directory)
        actual = Counter(name for kind, name in entries if name not in ('.', '..'))
        self.assertEqual(actual, Counter([*files, *directories]))
        for kind, name in entries:
            self.assertEqual(kind == '1', name in directories or name in ('.', '..'),
                             'name and directory type must describe the same entry: ' + name)

    def test_empty_directory_and_repeated_eof(self):
        self.check_entries()

    def test_one_file_returned_once(self):
        self.check_entries(['one.ttf'])

    def test_mixed_names_and_types(self):
        self.check_entries(['a.ttf', 'middle text.txt', 'z.otf'], ['b-folder', 'y-folder'])

    def test_long_filename_returned_intact_once(self):
        self.check_entries(['f' * 160 + '.otf'])

    def test_independent_directory_handles(self):
        (self.directory / 'font.ttf').write_text('normal fixture')
        self.run_directory('independent', self.directory)

    def test_missing_directory_returns_enoent(self):
        self.run_directory('missing', self.directory / 'not-present')

    def test_file_as_directory_reports_failure(self):
        path = self.directory / 'ordinary-file'
        path.write_text('normal fixture')
        # Preserve this wrapper's generic mapping for other Win32 open errors.
        self.run_directory('not-directory', path)


if __name__ == '__main__':
    unittest.main()
