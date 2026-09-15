# xkbcomp 1.5.0 in ZzXsrv

Imported from the official X.Org release archive on 2026-09-15.
`source-files.json` records the archive URL, SHA-256, every upstream file hash,
the imported file hashes and the generated-parser path mapping.

This is a modified distribution. `patches/windows.patch` records local Windows
adaptations, including binary XKM input. The local mhmake/Bison integration
regenerates the parser from xkbparse.y; upstream-generated/xkbparse.c is retained
as release evidence and is not compiled. The executable reports version 1.5.0.

License: COPYING. Validation and limitations:
docs/validation/2026-09-15-r8-dependencies.md in the ZzXsrv repository.
