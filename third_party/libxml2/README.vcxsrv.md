# libxml2 native source integration

`source/` contains the complete, unmodified libxml2 2.15.4 release archive.

- Source: https://download.gnome.org/sources/libxml2/2.15/libxml2-2.15.4.tar.xz
- SHA-256: `98087fd181d9070724f3fbc65c7377db03038eb92bd882374daff44940138821`
- Matched published digest: https://download.gnome.org/sources/libxml2/2.15/libxml2-2.15.4.sha256sum
- License: `source/Copyright`, with file-specific notices retained.
- Imported file hashes: `source-files.json`; preserve raw vendor bytes using `.gitattributes`.

ZzXsrv builds the DLL locally using MSVC and CMake, with GNU libiconv 1.19
and the repository's zlib. Use `scripts/build/buildall.ps1` from the repository
root. Build definitions live outside the unmodified source directory.
The build does not download dependencies.

The former inherited 2.9.1 DLLs and headers are superseded as a unit; they
must not be mixed with this release. Their historical version and unresolved
binary origin are documented in `docs/validation/2026-09-15-libxml2-assessment.md`.
The application provides HTTP configuration loading through Windows WinHTTP,
because this release no longer includes an HTTP client.

Repository and complete integration sources: https://github.com/jackfahdin/ZzXsrv
Build target: `third_party/libxml2/build/<Architecture>/<Configuration>/`.
