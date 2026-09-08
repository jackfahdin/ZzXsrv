#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR X11
#
# Copyright © 2024 Enrico Weigelt, metux IT consult <info@metux.net>

"""Native Python equivalent of generate-atoms for the predefined atom table."""

import argparse
from pathlib import Path


HEADER = '''/* THIS IS A GENERATED FILE
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
'''


def generate(source, output):
    lines = [HEADER]
    for line in source.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] == "@":
            name = fields[0]
            lines.append(f'    if (MakeAtom("{name}", {len(name)}, 1) != XA_{name})\n')
            lines.append("        AtomError();\n")
    lines.append("}\n")
    # Read and render completely before opening the destination, so a missing
    # or unreadable input never truncates a previously generated file.
    output.write_bytes("".join(lines).encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    try:
        generate(arguments.input, arguments.output)
    except (OSError, UnicodeError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
