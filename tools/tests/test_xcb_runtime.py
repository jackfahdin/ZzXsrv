"""Real Winsock options and XCB/Xlib calls through an authenticated server."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(os.environ.get('VCXSRV_TEST_XCB_BUILD_ROOT', ROOT))
spec = importlib.util.spec_from_file_location('xcb_runtime_tool', ROOT / 'tools/verify_runtime.py')
runtime_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_tool)


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS')
                     and os.environ.get('VCXSRV_TEST_RUNTIME') == '1',
                     'enable local tools and actual runtime tests')
class XcbRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = Path(os.environ['VCXSRV_RUNTIME_DIR'])
        cls.temp = tempfile.TemporaryDirectory(prefix='r9 xcb runtime ')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'xcb_consumer.exe'
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('x64 MSVC compiler required')
        for dll in cls.runtime.glob('*.dll'):
            shutil.copy2(dll, cls.work)
        command = [compiler, '/nologo', '/W4', '/WX', '/MD', '/DWIN32', '/D_WINDOWS',
                   '/I' + str(BUILD / 'include'), '/I' + str(BUILD / 'third_party/pthreads'),
                   ROOT / 'tools/tests/native/xcb_consumer.c',
                   BUILD / 'third_party/xorg/libxcb/src/obj64/release/libxcb.lib',
                   BUILD / 'third_party/xorg/libX11/obj64/release/libX11.lib',
                   'ws2_32.lib', '/Fe:' + str(cls.exe)]
        result = subprocess.run(list(map(str, command)), cwd=cls.work, capture_output=True,
                                text=True, errors='replace', timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def check_client(self, mode):
        with tempfile.TemporaryDirectory(prefix='r9 xcb evidence ') as directory:
            output = Path(directory)
            original = runtime_tool.run_command
            results = []

            def run_with_client(args, *positional, **keywords):
                code = original(args, *positional, **keywords)
                if Path(args[0]).name.lower() == 'xwininfo.exe' and code == 0:
                    runtime, env = positional[:2]
                    results.append(original([self.exe, args[2], mode], runtime, env,
                        output, 'xcb-client', 15, runtime_tool.step_record('xcb_client')))
                return code

            # Reuse the real authority/startup/cleanup path and add a client;
            # no socket, protocol reply or DLL API is mocked.
            with patch.object(runtime_tool, 'run_command', side_effect=run_with_client):
                steps = runtime_tool.run_smoke(self.runtime, output, 97, 30)
            self.assertTrue(all(s['status'] == 'PASS' for s in steps), steps)
            logs = '\n'.join(p.read_text(errors='replace') for p in output.glob('xcb-client.*.log'))
            self.assertEqual(results, [0], logs)
            self.assertIn('XCB consumer PASS', logs)

    def test_tcp_nodelay_enabled(self):
        self.check_client('nodelay')

    def test_tcp_keepalive_enabled(self):
        self.check_client('keepalive')

    def test_root_geometry(self):
        self.check_client('geometry')

    def test_xlib_and_xcb_share_atoms_and_root(self):
        self.check_client('xlib')

    def test_resource_identifiers_are_unique(self):
        self.check_client('ids')
