# Fontconfig 2.18.3 for the native Windows build

Official release:
https://gitlab.freedesktop.org/api/v4/projects/890/packages/generic/fontconfig/2.18.3/fontconfig-2.18.3.tar.xz

SHA-256: `4f7b554a38cdf78c033f666c8871f3749e14a094f65a07f630c91ed0b43d35e3`.
The downloaded hash matches the official adjacent `.sha256sum`; no independent
signature verification is claimed. All 1060 regular archive files are imported.
`source-files.json` records raw hashes and retained inherited files separately;
`patches/windows-adaptations.patch` reproduces changes to upstream payloads.

The native build retains the static FreeType/libxml2 backend, Windows defaults,
and the previously tested directory enumeration/invalid-handle corrections.
It adds fcconffile.c, fcgenericalias.c, generated constant and generic-family
tables, MSVC locale formatting, and 93 language definitions in upstream order.
The public header is generated from fontconfig.h.in with cache=12, minimum=9,
snapshot=0 and next=0. Gperf output is adapted to the native pointer/length types.
The checked-in header and native version macros both report 2.18.3.

Cache format 12 uses separate filenames. No symlink compatibility or cache
cleanup is enabled; existing format-9 caches are left in place. New-version
scans can create their own caches. The packaged fonts.conf remains unchanged.
The optional legacy user includes in upstream 50-user.conf are retained.

Old local build files, UUID support and ancillary CI/test files not present in
the release are explicitly inventoried as inherited files. Their presence does
not claim that the inherited CI/test or Meson/Rust paths were validated.
The historical synchronization SHA 25f58a52b0b30efbba0ea27c98dc58e411a42b84 was
not independently verified. Comparison with the official 2.16.0 tag identifies
old adaptations; that inherited tree was not a pristine 2.16.0 release.

Validation targets the existing x64 Release application. Full upstream tests,
Win32/Debug/Fontations, and installer execution are outside this validation.
