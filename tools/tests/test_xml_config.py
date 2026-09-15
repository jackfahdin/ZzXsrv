"""Exercise XLaunch's real CConfig XML load path with local and loopback inputs."""
import gzip
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]


def document(program="中文程序𠀀", encoding="UTF-8", declare_encoding=True):
    declaration = ('<?xml version="1.0" encoding="%s"?>' % encoding
                   if declare_encoding else '<?xml version="1.0"?>')
    text = (declaration +
            '<XLaunch Display=":27" LocalProgram="%s" '
            'RemoteProgram="远程程序" Clipboard="False"/>') % program
    codec = {"GBK": "gbk", "GB18030": "gb18030", "UTF-16": "utf-16"}.get(encoding, "utf-8")
    return text.encode(codec)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/direct")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/missing":
            body = b"not found"
            self.send_response(404)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path in ("/charset", "/charset-quoted"):
            body = document("中文程序", "GBK", declare_encoding=False)
            content_type = ("application/xml; Charset = \"GBK\"; profile=test"
                            if self.path == "/charset-quoted"
                            else "application/xml; charset=GBK")
        elif self.path == "/unrelated-charset-parameter":
            body = document()
            content_type = 'application/xml; profile="charset=GBK"'
        elif self.path == "/charset-precedence":
            text = ('<?xml version="1.0" encoding="UTF-8"?>'
                    '<XLaunch Display=":27" LocalProgram="中文程序" '
                    'RemoteProgram="远程程序" Clipboard="False"/>')
            body = text.encode("gbk")
            content_type = "application/xml; charset=GBK"
        else:
            body = document()
            content_type = "application/xml"
        if self.path == "/compressed":
            body = gzip.compress(body)
            content_encoding = "gzip"
        elif self.path == "/deflated":
            compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
            body = compressor.compress(body) + compressor.flush()
            content_encoding = "deflate"
        else:
            content_encoding = None
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        if content_encoding:
            self.send_header("Content-Encoding", content_encoding)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


@unittest.skipUnless(os.name == "nt" and os.environ.get("VCXSRV_TEST_LOCAL_TOOLS"),
                     "enable local tools in an x64 MSVC developer environment")
class XmlConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cl.exe")
        if not compiler:
            raise RuntimeError("cl.exe missing: use an x64 MSVC developer environment")
        cls.temp = tempfile.TemporaryDirectory(prefix="vcxsrv_xml_config_")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        libdir = Path(os.environ.get("VCXSRV_TEST_LIBXML_DIR",
                      ROOT / "third_party/libxml2/build/x64/Release"))
        runtimedir = Path(os.environ.get("VCXSRV_TEST_LIBXML_RUNTIME_DIR", libdir))
        include = Path(os.environ.get("VCXSRV_TEST_LIBXML_INCLUDE",
                       ROOT / "third_party/libxml2/source/include"))
        generated = Path(os.environ.get("VCXSRV_TEST_LIBXML_GENERATED_INCLUDE",
                         libdir / "include"))
        iconvdir = Path(os.environ.get("VCXSRV_TEST_ICONV_DIR",
                        ROOT / "third_party/libiconv/build/x64/Release"))
        zlibdir = Path(os.environ.get("VCXSRV_TEST_ZLIB_DIR",
                       ROOT / "third_party/zlib/obj64/release"))
        library_name = os.environ.get("VCXSRV_TEST_LIBXML_LIBRARY", "libxml2.lib")
        dll_name = os.environ.get("VCXSRV_TEST_LIBXML_DLL", "libxml2.dll")
        iconv_dll = os.environ.get("VCXSRV_TEST_ICONV_DLL", "libiconv.dll")
        zlib_dll = os.environ.get("VCXSRV_TEST_ZLIB_DLL", "zlib1.dll")
        legacy = bool(os.environ.get("VCXSRV_TEST_XML_CONFIG_LEGACY"))
        required = [libdir / library_name, runtimedir / dll_name,
                    include / "libxml/parser.h", generated / "libxml/xmlversion.h",
                    iconvdir / iconv_dll, zlibdir / zlib_dll]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise RuntimeError("missing XML test build outputs:\n" + "\n".join(missing))
        exe = cls.work / "xml_config.exe"
        config_source = ROOT / "src/xorg-server/hw/xwin/xlaunch/config.cc"
        if legacy:
            legacy_source = cls.work / "config_legacy.cc"
            legacy_source.write_text(config_source.read_text().replace(
                '#include "xml_input.h"', '').replace(
                'xlaunchReadXml(filename)', 'xmlReadFile(filename, NULL, 0)'))
            config_source = legacy_source
        sources = [ROOT / "tools/tests/native/xml_config.cpp", config_source]
        optional = ROOT / "src/xorg-server/hw/xwin/xlaunch/xml_input.cpp"
        if optional.exists() and not legacy:
            sources.append(optional)
        command = [compiler, "/nologo", "/std:c++14", "/EHsc", "/MD",
                   "/I" + str(ROOT / "src/xorg-server/hw/xwin/xlaunch"),
                   "/I" + str(ROOT / "include"),
                   "/I" + str(include), "/I" + str(generated),
                   *map(str, sources), "/Fe:" + str(exe),
                   "/link", "/LIBPATH:" + str(libdir), library_name, "winhttp.lib"]
        result = subprocess.run(command, cwd=cls.work, capture_output=True, text=True,
                                errors="replace", timeout=120)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        cls.exe = exe
        cls.env = os.environ.copy()
        cls.env["PATH"] = os.pathsep.join((str(runtimedir), str(iconvdir), str(zlibdir),
                                           cls.env.get("PATH", "")))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.thread.join, 5)
        cls.addClassCleanup(cls.server.server_close)
        cls.addClassCleanup(cls.server.shutdown)

    def run_config(self, source, expected_program="中文程序𠀀", success=True,
                   roundtrip=False, populated=False):
        args = [str(self.exe)]
        if populated:
            args.append("--populated")
        args.append(str(source))
        if roundtrip:
            args.append(str(self.work / "roundtrip.xlaunch"))
        result = subprocess.run(args, env=self.env, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=20)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.splitlines(), [":27", expected_program, "远程程序", "False"])
        else:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            expected = ([":88", "keep-local", "keep-remote", "False"] if populated else
                        ["-1", "xcalc", "xterm", "True"])
            self.assertEqual(result.stdout.splitlines(), expected)

    def write(self, name, data):
        path = self.work / name
        path.write_bytes(data)
        return path

    def test_plain_chinese_path_and_roundtrip(self):
        self.run_config(self.write("配置 文件.xlaunch", document()), roundtrip=True)

    def test_utf16(self):
        self.run_config(self.write("utf16.xlaunch", document(encoding="UTF-16")))

    def test_gbk(self):
        self.run_config(self.write("gbk.xlaunch", document("中文程序", "GBK")), "中文程序")

    def test_gb18030_extended_character(self):
        self.run_config(self.write("gb18030.xlaunch", document(encoding="GB18030")))

    def test_gzip_file(self):
        self.run_config(self.write("config.xlaunch.gz", gzip.compress(document())))

    def url(self, path):
        return "http://127.0.0.1:%d%s" % (self.server.server_port, path)

    def test_http_direct(self):
        self.run_config(self.url("/direct"))

    def test_http_redirect(self):
        self.run_config(self.url("/redirect"))

    def test_http_content_type_charset(self):
        self.run_config(self.url("/charset"), "中文程序")

    def test_http_content_type_quoted_charset(self):
        self.run_config(self.url("/charset-quoted"), "中文程序")

    def test_http_content_type_charset_overrides_xml_declaration(self):
        self.run_config(self.url("/charset-precedence"), "中文程序")

    def test_http_ignores_charset_text_in_unrelated_parameter(self):
        self.run_config(self.url("/unrelated-charset-parameter"))

    def test_http_gzip_response(self):
        self.run_config(self.url("/compressed"))

    def test_http_deflate_response(self):
        self.run_config(self.url("/deflated"))

    def test_http_404_does_not_change_defaults(self):
        self.run_config(self.url("/missing"), success=False)

    def test_http_404_preserves_existing_configuration(self):
        self.run_config(self.url("/missing"), success=False, populated=True)


if __name__ == "__main__":
    unittest.main()
