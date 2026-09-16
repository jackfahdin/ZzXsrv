# Pixman 0.46.4 for the native Windows build

Source: https://www.cairographics.org/releases/pixman-0.46.4.tar.xz

The archive contains 207 regular files and 17 relative symlinks. The links
are materialized as files for Windows; their original targets are recorded
in source-files.json. All 224 resulting files are imported: 218 retain upstream bytes,
while six carry the inherited, explicitly recorded adaptations in
`patches/windows-adaptations.patch`. `source-files.json` records raw archive,
upstream, current-file and patch hashes. The downloaded SHA-512 matches the
checksum published alongside the official archive; no independent PGP
signature verification is claimed.

Preserved adaptations: undefine the Windows IN macro in the compiler header;
keep the wider trapezoid step intermediate; preserve the glyph hash mask,
explicit pointer assertion, and inherited MMX/SSE2 narrowing adjustments.
These are retained compatibility changes, not six newly discovered defects.
Upstream changes to glyph allocation and other release files remain intact.

The three native-only files are pixman/makefile, pixman/pixman-config.h and
pixman/pixman-version.h. The version header is generated from the official
0.46.4 template, fixing the inherited 0.19.1 runtime/header report (the old
source declared 0.44.3). Package-version config values are synchronized; the
existing feature macros are retained. The native build includes the new
pixman-region64f.c and the previously omitted pixman-filter.c. pixman-region.c
remains an include template. Pixman is statically linked into the X server.

The previously recorded synchronization SHA
`aafb4caea2f440c8ca9fad2cfa2c2fb9e2779ae6` was not independently verified.
The original collection and comparison to official 0.44.2 remain documented
in the R9.3 validation report. They are not represented as a pristine release.

Validation targets x64 Release with existing SSE2 and scalar fallback paths.
x86/MMX, Debug, ARM, RISC-V and the full upstream suite are not claimed tested.
