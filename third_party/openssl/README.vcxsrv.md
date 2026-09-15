# OpenSSL 3.5.8 in ZzXsrv

Imported from the [official release archive](https://github.com/openssl/openssl/releases/download/openssl-3.5.8/openssl-3.5.8.tar.gz), released 2026-08-25.
The 3.5 LTS series is supported through 2030-04-08 according to the
[official lifecycle](https://openssl-library.org/roadmap/).

- Archive SHA-256: `a8f84a39918ec6415ce765d9b429d313ba97b8143169c172e734b9514464f5b2`; matched both the official SHA-256 file and GitHub release asset digest. No independent local PGP signature verification was performed.
- Tag `openssl-3.5.8`: tag object `090eec6d3628aa0520bdf2cf97b063fafc34e7be`, commit `f4dc4d58b48d346a8270183f89acf826d459b0ca`, checked with `git ls-remote`.
- All 5767 official files retain their original bytes. `source-files.json` records their hashes. This README and that manifest are local additions.
- Repository-level Git attributes preserve upstream bytes; repository-level ignores cover the four local build directories without modifying the upstream ignore file.
- `scripts/build/buildall.ps1` retains the native Perl Configure / VC-WIN64A or VC-WIN32 build, shared DLLs, and serial OpenSSL make stage. Output mapping remains release64/debug64/release32/debug32.
- Windows production X Server uses the existing low-level SHA-1 API through `os/xsha1.c` for glyph hashing. OpenSSL 3.x retains this API; this import does not migrate that wrapper to EVP.
- Existing link inputs include libssl, but the product only packages libcrypto. No TLS/QUIC feature or FIPS mode is enabled by this integration.
- License: `LICENSE.txt` (Apache-2.0). Packaging includes it and this source note.

The inherited 3.4.1 provenance remains historical in `docs/dependencies/SOURCES.json`.
Build, runtime and manual acceptance evidence is recorded separately in the R7 validation report.
