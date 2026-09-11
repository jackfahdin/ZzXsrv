"""Compile actual private auth I/O routines and test binary byte preservation."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]

@unittest.skipUnless(os.name=='nt' and os.environ.get('VCXSRV_TEST_LOCAL_TOOLS'),
                     'enable local tools in an x64 MSVC developer environment')
class AuthBinaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler=shutil.which('cl.exe')
        if not compiler: raise RuntimeError('cl.exe missing')
        cls.temp=tempfile.TemporaryDirectory(prefix='vcxsrv_auth_io_')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work=Path(cls.temp.name)
        source=(ROOT/'third_party/xorg/apps/xauth/process.c').read_text()
        declaration=re.search(r'typedef struct _AuthList \{.*?\} AuthList;',source,re.S)
        start=source.index('static int\nwrite_auth_file(')
        end=source.index('\nint\nauth_finalize(',start)
        template=(ROOT/'tools/tests/native/auth_binary.c.in').read_text()
        generated=template.replace('@AUTH_LIST@',declaration.group()).replace('@WRITE_AUTH_FILE@',source[start:end])
        cfile=cls.work/'auth_binary.c'; cfile.write_text(generated)
        includes=['.','include','third_party/pthreads','third_party/graphics/pixman/pixman',
                  'src/xorg-server','src/xorg-server/include','src/xorg-server/os',
                  'third_party/xorg/libXau']
        defines=['WIN32','_WINDOWS','WINDOWS','_MBCS','__i386__','__MINGW32__','_POSIX_',
                 'X_NOT_POSIX','_TIMEVAL_DEFINED','mode_t=int','__STDC__','FAKEIT',
                 'HAVE_CONFIG_H','_BSD_SOURCE','_WIN32_WINNT=0x0601','HAVE_DIX_CONFIG_H','PIXMAN_API=']
        cls.exe=cls.work/'auth_binary.exe'
        command=[compiler,'/nologo','/std:c11','/Od','/Gy','/Gw','/MD','/Zi','/fsanitize=address',
                 *['/I'+str(ROOT/p) for p in includes],*['/D'+d for d in defines],str(cfile),
                 '/Fe:'+str(cls.exe),'/link','/OPT:REF','/INCREMENTAL:NO']
        result=subprocess.run(command,cwd=cls.work,capture_output=True,text=True,errors='replace',timeout=120)
        print('COMPILE '+subprocess.list2cmdline(command),flush=True)
        print(result.stdout+result.stderr,flush=True)
        if result.returncode: raise RuntimeError(result.stdout+result.stderr)

    def run_case(self,mode,case):
        with tempfile.TemporaryDirectory(dir=self.work) as directory:
            result=subprocess.run([str(self.exe),mode,case],cwd=directory,capture_output=True,
                                  text=True,errors='replace',timeout=10)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS '+mode+' '+case,result.stdout)

    def test_write_control(self): self.run_case('write','control')
    def test_write_lf(self): self.run_case('write','lf')
    def test_write_crlf(self): self.run_case('write','crlf')
    def test_write_ctrlz(self): self.run_case('write','ctrlz')
    def test_write_all_bytes(self): self.run_case('write','all')
    def test_read_control(self): self.run_case('read','control')
    def test_read_lf(self): self.run_case('read','lf')
    def test_read_crlf(self): self.run_case('read','crlf')
    def test_read_ctrlz(self): self.run_case('read','ctrlz')
    def test_read_all_bytes(self): self.run_case('read','all')
