"""Contracts for the native libiconv/libxml2 dependency build."""

import json
import os
from pathlib import Path
import re
import subprocess
import shutil
import unittest


ROOT = Path(__file__).resolve().parents[2]
BUILD_XML = ROOT / "scripts/build/buildxml.ps1"
def find_cmake():
    explicit = os.environ.get("VCXSRV_TEST_CMAKE")
    if explicit:
        return Path(explicit)
    vs_root = os.environ.get("VSINSTALLDIR")
    if vs_root:
        bundled = Path(vs_root) / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
        if bundled.is_file():
            return bundled
    vswhere = Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft Visual Studio/Installer/vswhere.exe"
    if vswhere.is_file():
        query = subprocess.run(
            [str(vswhere), "-latest", "-products", "*", "-version", "[17.0,18.0)",
             "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
             "-property", "installationPath"],
            capture_output=True, text=True,
        )
        if query.returncode == 0 and query.stdout.strip():
            bundled = Path(query.stdout.strip()) / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
            if bundled.is_file():
                return bundled
    found = shutil.which("cmake.exe")
    return Path(found) if found else None


CMAKE = find_cmake()


@unittest.skipUnless(os.name == "nt", "requires Windows PowerShell")
class XmlBuildPlanTests(unittest.TestCase):
    def get_plan(self, architecture, configuration):
        self.assertIsNotNone(CMAKE, "set VCXSRV_TEST_CMAKE or install CMake")
        self.assertTrue(CMAKE.is_file(), f"missing CMake: {CMAKE}")
        result = subprocess.run(
            [
                "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(BUILD_XML), "-CheckOnly", "-CMakePath", str(CMAKE),
                "-Architecture", architecture, "-Configuration", configuration,
            ],
            cwd=ROOT.parent,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_check_only_reports_reproducible_native_build_contract(self):
        plan = self.get_plan("x64", "Release")
        self.assertEqual(plan["target"], {"architecture": "x64", "configuration": "Release"})
        self.assertEqual(Path(plan["cmake"]), CMAKE)
        self.assertEqual(
            Path(plan["iconv"]["source"]), ROOT / "third_party/libiconv/source"
        )
        self.assertEqual(
            {Path(path).name for path in plan["iconv"]["outputs"]},
            {"libiconv.dll", "libiconv.lib"},
        )
        self.assertEqual(
            {Path(path).name for path in plan["libxml2"]["outputs"]},
            {"libxml2.dll", "libxml2.lib"},
        )
        self.assertEqual(plan["libxml2"]["features"], {
            "iconv": True, "output": True, "push": True, "sax1": True,
            "threads": True, "tree": True, "zlib": True,
        })
        self.assertEqual(
            Path(plan["zlib_library"]),
            ROOT / "third_party/zlib/obj64/release/zlib1.lib",
        )
        configure = set(plan["libxml2"]["configure"])
        for flag in (
            "-DBUILD_SHARED_LIBS=ON", "-DLIBXML2_WITH_ICONV=ON",
            "-DLIBXML2_WITH_ZLIB=ON", "-DLIBXML2_WITH_OUTPUT=ON",
            "-DLIBXML2_WITH_PUSH=ON", "-DLIBXML2_WITH_SAX1=ON",
            "-DLIBXML2_WITH_THREADS=ON", "-DLIBXML2_WITH_TESTS=OFF",
            "-DLIBXML2_WITH_PYTHON=OFF", "-DLIBXML2_WITH_PROGRAMS=OFF",
        ):
            self.assertIn(flag, configure)

    def test_all_supported_output_mappings(self):
        for architecture, configuration, zlib_part in (
            ("x64", "Release", "obj64/release"),
            ("x64", "Debug", "obj64/debug"),
            ("Win32", "Release", "obj/release"),
            ("Win32", "Debug", "obj/debug"),
        ):
            with self.subTest(architecture=architecture, configuration=configuration):
                plan = self.get_plan(architecture, configuration)
                expected = Path("third_party/libxml2/build") / architecture / configuration
                self.assertEqual(
                    Path(plan["libxml2"]["outputs"][0]).relative_to(ROOT),
                    expected / "libxml2.dll",
                )
                self.assertEqual(
                    Path(plan["zlib_library"]).relative_to(ROOT),
                    Path("third_party/zlib") / zlib_part / "zlib1.lib",
                )


class XmlRepositoryIntegrationTests(unittest.TestCase):
    def test_make_variables_select_native_outputs_and_generated_headers(self):
        makefile = (ROOT / "makefile.before").read_text(encoding="utf-8")
        self.assertIn(
            r"LIBXMLLIB:=$(COMPONENT_LIBXML2_DIR)\build\$(XMLARCH)\$(XMLCONFIG)\libxml2.lib",
            makefile,
        )
        self.assertIn(
            r"LIBXMLINCLUDE:=$(COMPONENT_LIBXML2_DIR)\build\$(XMLARCH)\$(XMLCONFIG)\include",
            makefile,
        )

    def test_installers_stage_only_native_xml_runtime_pair(self):
        manifests = sorted((ROOT / "src/xorg-server/installer").glob("vcxsrv*.nsi"))
        self.assertEqual(len(manifests), 4)
        for manifest in manifests:
            with self.subTest(manifest=manifest.name):
                text = manifest.read_text(encoding="utf-8-sig")
                xml_files = {
                    Path(match.replace("\\", "/")).name
                    for match in re.findall(r'^\s*File\s+"([^"]*(?:libxml|libiconv|libgcc|libwinpthread)[^"]*\.dll)"', text, re.M | re.I)
                }
                self.assertEqual(xml_files, {"libxml2.dll", "libiconv.dll"})


if __name__ == "__main__":
    unittest.main()
