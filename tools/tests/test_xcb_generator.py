"""Compile real generator output and inspect normal FD request assembly."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
XCB = ROOT / 'third_party/xorg/libxcb'


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable native compiler tests')
class XcbGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='r9 xcb generator ')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'fd_consumer.exe'
        cls.run_checked([sys.executable, '-B', XCB / 'src/c_client.py', '-c', 'test',
            '-l', 'test', '-s', '3', '-p', XCB / 'xcb-proto',
            ROOT / 'tools/tests/native/xcb_fd_contract.xml'])
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('x64 MSVC environment required')
        cls.run_checked([compiler, '/nologo', '/MD', '/DWIN32', '/D_WINDOWS', '/DLIBXCB_DLL',
            '/I' + str(cls.work), '/I' + str(ROOT / 'include'),
            '/I' + str(ROOT / 'include/xcb'), '/I' + str(ROOT / 'third_party/pthreads'),
            '/FI' + str(ROOT / 'tools/tests/native/xcb_fd_alloc_hook.h'),
            cls.work / 'xcb_fd_contract.c', ROOT / 'tools/tests/native/xcb_fd_consumer.c',
            '/Fe:' + str(cls.exe)])

    @classmethod
    def run_checked(cls, command):
        result = subprocess.run(list(map(str, command)), cwd=cls.work, capture_output=True,
                                text=True, errors='replace', timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def check_request(self, mode):
        result = subprocess.run([str(self.exe), mode], cwd=self.work, capture_output=True,
                                text=True, errors='replace', timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), 'XCB FD generator PASS')

    def test_one_fixed_descriptor(self):
        self.check_request('fixed')

    def test_four_descriptor_array(self):
        self.check_request('array')

    def test_fixed_plus_two_descriptor_array(self):
        self.check_request('mixed')
