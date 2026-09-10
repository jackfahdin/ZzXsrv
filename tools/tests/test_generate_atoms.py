"""Check the real atom generator CLI against protocol data and small fixtures."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
XORG_SERVER = ROOT / "src" / "xorg-server"
GENERATOR = XORG_SERVER / "dix" / "generate-atoms.py"


class GenerateAtomsTests(unittest.TestCase):
    def invoke(self, source, output):
        return subprocess.run(
            [sys.executable, str(GENERATOR), str(source), str(output)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )

    def test_only_second_token_marker_rows_generate_in_input_order(self):
        with tempfile.TemporaryDirectory(prefix="atoms test ") as temporary:
            source = Path(temporary) / "atoms input"
            output = Path(temporary) / "initatoms.c"
            source.write_bytes(b"comment contains @ somewhere\r\nZZ @\nA\t@ trailing tokens\r\nB @@\n  LONG_NAME  @\n@\n")
            result = self.invoke(source, output)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            expected = '''/* THIS IS A GENERATED FILE
 *
 * Do not change!  Changing this file implies a protocol change!
 */

#ifdef HAVE_DIX_CONFIG_H
#include <dix-config.h>
#endif

#include <X11/X.h>
#include <X11/Xatom.h>

#include "dix/dix_priv.h"

#include "misc.h"
#include "dix.h"
void
MakePredeclaredAtoms(void)
{
    if (MakeAtom("ZZ", 2, 1) != XA_ZZ)
        AtomError();
    if (MakeAtom("A", 1, 1) != XA_A)
        AtomError();
    if (MakeAtom("LONG_NAME", 9, 1) != XA_LONG_NAME)
        AtomError();
}
'''
            self.assertEqual(output.read_bytes(), expected.encode("ascii"))

    def test_repository_atoms_match_predefined_protocol_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "initatoms.c"
            result = self.invoke(XORG_SERVER / "dix" / "BuiltInAtoms", output)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            content = output.read_text(encoding="ascii")
            atoms = re.findall(r'MakeAtom\("([A-Z0-9_]+)", (\d+), 1\) != XA_([A-Z0-9_]+)', content)
            self.assertEqual(len(atoms), 68)
            self.assertEqual(atoms[0], ("PRIMARY", "7", "PRIMARY"))
            self.assertEqual(atoms[-1], ("WM_TRANSIENT_FOR", "16", "WM_TRANSIENT_FOR"))
            self.assertEqual(content.count("AtomError();"), 68)
            protocol = (ROOT / "include" / "X11" / "Xatom.h").read_text(encoding="ascii")
            last_predefined = re.search(r"#define XA_LAST_PREDEFINED\s+\(\(Atom\)\s*(\d+)\)", protocol)
            self.assertIsNotNone(last_predefined)
            self.assertEqual(len(atoms), int(last_predefined.group(1)))
            for name, length, constant in atoms:
                self.assertEqual(name, constant)
                self.assertEqual(len(name), int(length))

    def test_missing_input_leaves_existing_output_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "initatoms.c"
            output.write_bytes(b"previous successful output")
            result = self.invoke(Path(temporary) / "missing", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"error:", result.stderr.lower())
            self.assertEqual(output.read_bytes(), b"previous successful output")


if __name__ == "__main__":
    unittest.main()
