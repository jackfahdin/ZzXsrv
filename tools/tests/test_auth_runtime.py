"""Opt-in checks of binary authority data in the built client and server."""
import importlib.util
import os
from pathlib import Path
import secrets
import struct
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('auth_runtime_tool',Path(__file__).resolve().parents[1]/'verify_runtime.py')
runtime_tool=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_tool)

def authority_cookie(record):
    """Read the wire framing; xauth may canonicalize loopback as FamilyLocal."""
    offset=2
    fields=[]
    for _ in range(4):
        length=struct.unpack_from('>H',record,offset)[0]
        offset+=2
        fields.append(record[offset:offset+length])
        offset+=length
    if offset!=len(record) or fields[1]!=b'97' or fields[2]!=b'MIT-MAGIC-COOKIE-1':
        raise AssertionError('authority must contain one complete framed record')
    return fields[3]

@unittest.skipUnless(os.environ.get('VCXSRV_TEST_RUNTIME')=='1',
                     'set VCXSRV_TEST_RUNTIME=1 for authenticated desktop integration')
class AuthRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime=Path(os.environ['VCXSRV_RUNTIME_DIR'])
        cls.system32=runtime_tool.require_host()

    def test_xauth_writes_all_byte_values_exactly(self):
        with tempfile.TemporaryDirectory(prefix='vcxsrv auth bytes ') as directory:
            output=Path(directory)
            env=runtime_tool.child_environment(self.runtime,self.system32)
            # Byte values are file-format fixtures, never used to start a server.
            for start in range(0,256,16):
                with self.subTest(start=start):
                    cookie=bytes(range(start,start+16)); authority=output/f'authority-{start}'
                    step=runtime_tool.step_record('xauth')
                    code=runtime_tool.run_command([self.runtime/'xauth.exe','-f',authority,'add',
                        '127.0.0.1:97','.',cookie.hex()],self.runtime,env,output,f'add-{start}',10,step,secret=cookie.hex())
                    self.assertEqual(code,0)
                    self.assertEqual(authority_cookie(authority.read_bytes()),cookie)

    def check_cookie(self,fragment,wrong=False):
        # Keep 112+ random bits; never expose active cookie values in assertions.
        cookie=fragment+secrets.token_bytes(16-len(fragment))
        with tempfile.TemporaryDirectory(prefix='vcxsrv binary auth ') as directory:
            output=Path(directory)
            wrong_file=output/'wrong authority'
            wrong_value=bytes([cookie[0]^0xff])+cookie[1:]
            original=runtime_tool.run_command
            def checked_run(args,*positional,**keywords):
                if Path(args[0]).name.lower()=='xwininfo.exe' and wrong:
                    values=list(positional)
                    values[1]=dict(values[1],XAUTHORITY=str(wrong_file))
                    positional=tuple(values)
                code=original(args,*positional,**keywords)
                if Path(args[0]).name.lower()=='xauth.exe':
                    record=Path(args[2]).read_bytes()
                    self.assertTrue(authority_cookie(record)==cookie,
                                    'xauth must preserve authority bytes')
                    wrong_file.write_bytes(record[:-len(cookie)]+wrong_value)
                return code
            with patch.object(runtime_tool.secrets,'token_hex',return_value=cookie.hex()), \
                 patch.object(runtime_tool,'run_command',side_effect=checked_run):
                result=runtime_tool.run_smoke(self.runtime,output,97,3 if wrong else 30,self.system32)
            by_name={step['name']:step for step in result}
            self.assertEqual(by_name['cleanup']['status'],'PASS')
            if wrong:
                self.assertEqual(by_name['root_window']['status'],'FAIL')
                errors=''.join(p.read_text(errors='replace') for p in output.glob('client-*.stderr.log'))
                self.assertIn('Invalid MIT-MAGIC-COOKIE-1 key',errors)
            else:
                self.assertTrue(all(step['status']=='PASS' for step in result),
                                [(step['name'],step['status'],step['reason']) for step in result])

    def test_server_accepts_binary_cookies(self):
        for fragment in (b'\n',b'\r\n',b'\x1a'):
            with self.subTest(fragment=fragment): self.check_cookie(fragment)

    def test_server_rejects_wrong_cookie(self):
        self.check_cookie(b'\x1a',wrong=True)
