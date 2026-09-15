"""Check production SHA-1 objects against the DLL actually shipped to users.

VCXSRV_TEST_OPENSSL_BUILD_ROOT permits an explicit old-product comparison.
Normal runs use this worktree and VCXSRV_RUNTIME_DIR (or its own dist).
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'), 'enable native build tests')
class OpenSSLConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt' or not shutil.which('cl.exe'):
            raise RuntimeError('OpenSSL consumer tests need x64 MSVC')
        build = Path(os.environ.get('VCXSRV_TEST_OPENSSL_BUILD_ROOT', ROOT))
        ssl = build / 'third_party/openssl'
        runtime = Path(os.environ.get('VCXSRV_RUNTIME_DIR', build / 'dist/x64/Release'))
        cls.temp = tempfile.TemporaryDirectory(prefix='zzxsrv_openssl_')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'openssl_consumer.exe'
        # Keep the DLL next to the executable: PATH cannot select an older DLL.
        shutil.copy2(runtime / 'libcrypto-3-x64.dll', cls.work)
        cls.run_command([shutil.which('cl.exe'), '/nologo', '/W4', '/WX', '/MD',
                         '/D_CRT_SECURE_NO_WARNINGS',
                         '/I' + str(ssl / 'release64/include'), '/I' + str(ssl / 'include'),
                         '/I' + str(ROOT / 'src/xorg-server'),
                         ROOT / 'tools/tests/native/openssl_consumer.c',
                         build / 'src/xorg-server/os/obj64/servrelease/xsha1.obj',
                         ssl / 'release64/libcrypto.lib', '/Fe:' + str(cls.exe)])

    @classmethod
    def run_command(cls, command):
        result = subprocess.run([str(x) for x in command], cwd=cls.work,
                                capture_output=True, encoding='utf-8', errors='replace', timeout=120)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout

    def digest(self, data, zero_update=False):
        fixture = self.work / 'input.bin'
        fixture.write_bytes(data)
        arguments = [self.exe, fixture]
        if zero_update:
            arguments.append('zero-update')
        return self.run_command(arguments).strip()

    def test_packaged_runtime_version(self):
        self.assertEqual(self.run_command([self.exe, 'version']).strip(),
                         'OpenSSL 3.5.8 25 Aug 2026')

    def test_empty_input(self):
        self.assertEqual(self.digest(b''), 'da39a3ee5e6b4b0d3255bfef95601890afd80709')

    def test_short_input(self):
        self.assertEqual(self.digest(b'abc'), 'a9993e364706816aba3e25717850c26c9cd0d89d')

    def test_zero_length_update_preserves_digest(self):
        self.assertEqual(self.digest(b'abc', zero_update=True),
                         'a9993e364706816aba3e25717850c26c9cd0d89d')

    def test_multi_block_input(self):
        self.assertEqual(self.digest(b'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq'),
                         '84983e441c3bd26ebaae4aa1f95129e5e54670f1')

    def test_repeated_updates(self):
        self.assertEqual(self.digest(b'a' * 1000000),
                         '34aa973cd4c4daa4f61eeb2bdbad27316534016f')


if __name__ == '__main__':
    unittest.main()
