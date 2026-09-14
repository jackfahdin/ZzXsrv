"""Opt-in normal PCF/TrueType drawing through the actual authenticated server."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('font_runtime_tool', ROOT / 'tools/verify_runtime.py')
runtime_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_tool)


@unittest.skipUnless(os.name == 'nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS')
                     and os.environ.get('VCXSRV_TEST_RUNTIME') == '1',
                     'enable local tools and actual runtime tests')
class FontRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = Path(os.environ['VCXSRV_RUNTIME_DIR'])
        cls.temp = tempfile.TemporaryDirectory(prefix='zzxsrv font runtime ')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.exe = cls.work / 'font_runtime.exe'
        compiler = shutil.which('cl.exe')
        if not compiler:
            raise RuntimeError('x64 MSVC compiler is required')
        command = [compiler, '/nologo', '/MD', '/DWIN32', '/D_WINDOWS',
                   '/I' + str(ROOT / 'include'),
                   str(ROOT / 'tools/tests/native/font_runtime.c'),
                   str(ROOT / 'third_party/xorg/libX11/obj64/release/libX11.lib'),
                   '/Fe:' + str(cls.exe)]
        result = subprocess.run(command, cwd=cls.work, capture_output=True,
                                text=True, errors='replace', timeout=90)
        print('COMPILE ' + subprocess.list2cmdline(command), flush=True)
        print(result.stdout + result.stderr, flush=True)
        if result.returncode:
            raise RuntimeError('core-font client compilation failed')

    def check_font(self, name):
        with tempfile.TemporaryDirectory(prefix='zzxsrv font evidence ') as directory:
            output = Path(directory)
            original = runtime_tool.run_command
            results = []

            def run_with_font(args, *positional, **keywords):
                code = original(args, *positional, **keywords)
                if Path(args[0]).name.lower() == 'xwininfo.exe' and code == 0:
                    runtime, env = positional[:2]
                    step = runtime_tool.step_record('core_font')
                    result = original(
                        [self.exe, args[2], name], runtime, env, output,
                        'core-font', 15, step)
                    results.append(result)
                return code

            # Keep the existing authority/startup/cleanup path; only add a normal
            # Xlib client after the authenticated root query succeeds.
            with patch.object(runtime_tool, 'run_command', side_effect=run_with_font):
                steps = runtime_tool.run_smoke(self.runtime, output, 97, 30)
            self.assertTrue(all(s['status'] == 'PASS' for s in steps), steps)
            self.assertEqual(results, [0],
                             '\n'.join(p.read_text(errors='replace') for p in output.glob('core-font.*.log')))
            client_output = (output / 'core-font.stdout.log').read_text()
            print(client_output, flush=True)
            self.assertIn('PASS core font', client_output)

    def test_pcf_core_font_draws_pixels(self):
        self.check_font('-misc-fixed-medium-r-normal--13-120-75-75-c-70-iso8859-1')

    def test_truetype_core_font_draws_pixels(self):
        self.check_font('-bitstream-bitstream vera sans-medium-r-normal--16-0-0-0-p-0-iso8859-1')


if __name__ == '__main__':
    unittest.main()
