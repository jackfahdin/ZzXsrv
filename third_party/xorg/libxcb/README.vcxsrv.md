# libxcb and xcb-proto in ZzXsrv

Audited on 2026-09-16 against the official 1.17.0 release archives. The versions
remain 1.17.0. This is an inherited, modified source collection, not a new
replacement with pristine release contents. `source-audit.json` records raw
archive hashes, comparisons, omitted release-generated files and local files.
Local text hashes explicitly normalize CRLF to LF. Comparison patches include
both inherited changes and the current correction; they are not all new patches.

Windows socket/thread/DLL integration and protocol generation remain in place.
The local generator now allocates FD arrays in bytes using the element size,
including expressions that combine fixed and variable descriptor counts.
This does not add Unix FD-passing support or new DLL exports on Windows.

Utility sources embedded in src/ are kept separate from the libxcb release
comparison. Their exact upstream import versions remain unverified. The old
recorded synchronization commits remain historical evidence, not independently
verified upstream commit identities. No PGP verification is claimed.

Licenses: COPYING and xcb-proto/COPYING. See
docs/validation/2026-09-16-r9-xcb.md in the ZzXsrv repository for validation.
