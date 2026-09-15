# libX11 1.8.13 in ZzXsrv

Imported from the official X.Org release archive on 2026-09-15.
`source-files.json` records the archive URL, SHA-256, original file hashes,
imported file hashes and local build files. `patches/windows.patch` records
changes to upstream files. Archive bytes are preserved without normalization.

This is a modified distribution. Windows DLL exports, mhmake integration,
native file and locale handling, pointer-width conversions and server symbol
renaming are retained. Local config version metadata is updated to 1.8.13.
Three inherited patches already included upstream are not reapplied.
The installed X11 headers have the same content as these adapted headers;
upstream did not change their public content between 1.8.11 and 1.8.13.

License: COPYING. Validation and limitations:
docs/validation/2026-09-15-r9-libx11.md in the ZzXsrv repository.
