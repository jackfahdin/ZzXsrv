"""Plink runtime smoke tests against the built distribution."""
import os
from pathlib import Path
import struct
import unittest
import subprocess

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = Path(os.environ.get('VCXSRV_RUNTIME_DIR', ROOT / 'dist/x64/Release'))
PLINK = RUNTIME / 'plink.exe'


def pe_machine(path):
    data = path.read_bytes()
    assert data[:2] == b'MZ'
    offset = struct.unpack_from('<I', data, 0x3c)[0]
    assert data[offset:offset + 4] == b'PE\0\0'
    return struct.unpack_from('<H', data, offset + 4)[0]


@unittest.skipUnless(os.environ.get('VCXSRV_TEST_RUNTIME'), 'enable runtime tests')
class PlinkRuntimeTests(unittest.TestCase):
    def test_plink_exe_is_x64_pe(self):
        self.assertTrue(PLINK.is_file(), f'missing {PLINK}')
        self.assertEqual(pe_machine(PLINK), 0x8664, 'plink.exe is not an x64 PE')

    def test_version_reports_official_release(self):
        result = subprocess.run([str(PLINK), '-V'], capture_output=True, text=True,
                                errors='replace', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = result.stdout + result.stderr
        self.assertIn('Release 0.85', output)
        self.assertIn('64-bit x86 Windows', output)

    def test_unknown_option_fails(self):
        result = subprocess.run([str(PLINK), '--vcxsrv-no-such-option'],
                                capture_output=True, text=True, errors='replace',
                                timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unknown option', (result.stdout + result.stderr).lower())


if __name__ == '__main__':
    unittest.main()
