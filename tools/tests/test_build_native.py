"""Exercise the native build filters through their real byte-stream CLI."""

import gzip
from pathlib import Path
import subprocess
import sys
import unittest


HELPER = Path(__file__).resolve().parents[1] / "build_native.py"


class BuildNativeTests(unittest.TestCase):
    def run_filter(self, command, payload):
        result = subprocess.run(
            [sys.executable, str(HELPER), command],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stderr, b"")
        return result.stdout

    def test_gzip_roundtrips_all_byte_values(self):
        # Text-mode pipes would corrupt CR/LF, high bytes or Ctrl-Z on Windows.
        payload = bytes(range(256)) * 4097
        self.assertEqual(gzip.decompress(self.run_filter("gzip", payload)), payload)

    def test_gzip_has_reproducible_header_and_output(self):
        # A current timestamp or a source filename makes build artifacts vary.
        first = self.run_filter("gzip", b"same font data\r\n\x1a\xff")
        second = self.run_filter("gzip", b"same font data\r\n\x1a\xff")
        self.assertEqual(first, second)
        self.assertEqual(first[4:8], b"\x00\x00\x00\x00")
        self.assertEqual(first[3] & 0x08, 0, "gzip must omit the filename")

    def test_locale_aliases_applies_both_sed_expressions_in_order(self):
        # Covers comments, only-first-colon removal, deletion after whitespace,
        # the regex's significant first character, and unchanged line endings.
        payload = (
            b"# comment: keep this: too\r\n"
            b"alias: target\n"
            b"alias:: target\r\n"
            b"alias: target:drop\n"
            b"alias target:drop\r\n"
            b" alias: target\n"
            b"\talias:\ttarget\r\n"
            b"  alias: target\n"
            b" # comment:drop\n"
            b"\n"
            b"plain\tvalue\r\n"
            b"\xffname: value\n"
            b"last: value"
        )
        expected = (
            b"# comment: keep this: too\r\n"
            b"alias target\n"
            b"alias: target\r\n"
            b" alias target\n"
            b"\talias\ttarget\r\n"
            b"\n"
            b"plain\tvalue\r\n"
            b"\xffname value\n"
            b"last value"
        )
        self.assertEqual(self.run_filter("locale-aliases", payload), expected)

    def test_cut_out_removes_multiple_regions_and_their_marker_lines(self):
        # Missing state changes leak removed blocks or swallow later content.
        payload = (
            b"first\r\n"
            b"prefix CUT_OUT_BEGIN suffix\n"
            b"hidden one\r\n"
            b"CUT_OUT_BEGIN\n"
            b"hidden two\n"
            b"CUT_OUT_END\r\n"
            b"middle\n"
            b"CUT_OUT_END\n"
            b"CUT_OUT_BEGIN CUT_OUT_END\n"
            b"hidden three\n"
            b"CUT_OUT_END\n"
            b"last\xff\r\n"
        )
        self.assertEqual(self.run_filter("cut-out", payload), b"first\r\nmiddle\nlast\xff\r\n")

    def test_invalid_arguments_fail_without_producing_output(self):
        # Invalid invocations must fail clearly instead of generating a target.
        for arguments in ([], ["unknown"], ["gzip", "extra"]):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, str(HELPER), *arguments],
                    input=b"input",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"usage:", result.stderr.lower())

    def test_cut_out_terminates_a_kept_final_record_like_awk_print(self):
        # awk print adds its output separator even without a trailing input LF.
        self.assertEqual(self.run_filter("cut-out", b"last record"), b"last record\n")


if __name__ == "__main__":
    unittest.main()
