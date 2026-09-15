# zlib 1.3.2 in ZzXsrv

Imported from the official zlib release archive on 2026-09-15.
`source-files.json` records the archive URL, SHA-256, upstream hashes and imported
hashes. `patches/windows.patch` records all changes to upstream files.

This is a modified distribution: the root Makefile is the local mhmake file,
stdio includes and the Windows export list adapt the existing build, and MSVC
file flag aliases include binary and exclusive-open modes. The DLL remains
zlib1.dll with the existing C calling convention and adds the 1.3.2 interfaces.

This root library is separate from FreeType's embedded zlib and Meson fallback
declarations. contrib/minizip is not compiled into this Windows product.

License: LICENSE. Validation and limitations:
docs/validation/2026-09-15-r8-dependencies.md in the ZzXsrv repository.
