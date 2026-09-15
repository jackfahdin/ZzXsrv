# Expat 2.8.4 Windows integration

The 170 files listed in `source-files.json` are the complete official release
archive, preserved byte for byte (including the archive's generated files).

- Archive: https://github.com/libexpat/libexpat/releases/download/R_2_8_4/expat-2.8.4.tar.xz
- SHA-256: `656ae1cc8da3b4ea513bb4e254f33e6243938084c0ec6239da873376b09985a7`
- Digest matched the GitHub release asset `digest` field on 2026-09-15.
- Tag: `R_2_8_4`; tag object `6dd46f3d0fcaeda0af6d00fd496acb8fe96b900d`;
  peeled commit `12cf0b1f25f026a022fe728ad8f7e3d017285b80`, queried with `git ls-remote`.
- The archive signature was not independently verified locally.
- License: `COPYING`; individual source notices (including SipHash) are retained.

Local files outside that manifest are `lib/makefile`, `msvc/expat_config.h`,
this README, `.gitattributes`, and `source-files.json`. The mhmake build
selects `msvc/expat_config.h` before the archive's root configuration header.
It retains narrow `XML_Char`, DTD/general entities, namespaces, and 1024 context
bytes. XML_UNICODE, XML_LARGE_SIZE and XML_ATTR_INFO remain disabled.
Windows entropy uses upstream `random_rand_s.c`; no Unix entropy macros are set.

`scripts/build/buildall.ps1` builds the static library through Mesa's existing
dependency rule. Outputs remain `lib/obj64/release/libexpat.lib` for x64 Release,
with the existing mhmake architecture/configuration directory conventions.
The build does not download dependencies and introduces no Expat runtime DLL.

Mesa currently links this archive but does not enable WITH_XMLCONFIG on Windows:
`xmlconfig.c` uses its static configuration branch. Upgrading the library does
not enable external drirc XML loading or change the Mesa version. The inherited
2.6.2 library could not be linked independently because its root configuration
incorrectly enabled arc4random_buf. The new native API tests exercise the actual
archive and Windows entropy path, in addition to rebuilding the complete product.

The previous inherited source provenance remains historical evidence; it is not
retroactively attributed to this release. See `docs/validation/2026-09-15-expat.md`
in the repository for validation results and remaining scope.
