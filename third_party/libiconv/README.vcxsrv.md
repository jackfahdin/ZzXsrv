# GNU libiconv native source integration

`source/` starts from the complete GNU libiconv 1.19 release archive and adds
the eight Windows compatibility files listed below. The conversion tables
are unchanged from that official archive.

- Official source: https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.19.tar.gz
- SHA-256 (locally computed, no published digest/signature verification):
  `88dd96a8c0464eca144fc791ae60cd31cd8ee78321e67397e25fc095c4a19aa6`
- Windows adaptation: https://github.com/winlibs/libiconv/tree/accac417318a3eef7402685a268cab8037e62ba1
- Fixed ZIP: https://codeload.github.com/winlibs/libiconv/zip/accac417318a3eef7402685a268cab8037e62ba1
- ZIP SHA-256: `f1fed410a2a93570f1f669148664cecebbf816e2856e30e57926009b4286e101`
- Library license: `source/COPYING.LIB` (GNU LGPL 2.1); preserve individual file
  notices, including their later-version permissions. `source/COPYING` is
  retained for the other source package material.

Modified official files: `lib/aliases.h`, `lib/canonical.h`,
`lib/canonical_dos.h`, `lib/canonical_local.h`, `lib/iconv.c`.
Added generated/configuration headers: `config.h`, `include/iconv.h`,
`lib/localcharset.h`. The Winlibs backup `lib/aliases.h.orig` is not imported.
`msvc-compat.patch` records the normalized textual difference;
`source-files.json` records all 1112 imported files' raw SHA-256 values.
`.gitattributes` preserves raw vendor bytes across checkouts.

The public `include/iconv.h` at the ZzXsrv repository root is synchronized
with this version. Builds compile `lib/iconv.c`,
`libcharset/lib/localcharset.c`, and `lib/compat.c` as a DLL, using the native
Windows CRT. The Winlibs project and its cleanup/packaging commands are not
used by the production build. The repository's separate build definition
enables address randomization and selects the requested architecture and CRT.

Build with `scripts/build/buildall.ps1`; no dependencies are downloaded during
the build. Output: `third_party/libiconv/build/<Architecture>/<Configuration>/`.
Repository and complete integration sources: https://github.com/jackfahdin/ZzXsrv
