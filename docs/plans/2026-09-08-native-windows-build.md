# Native Windows build implementation plan

> 目录迁移说明（2026-09-10）：文档链接已更新，正文中的旧命令与文件路径仍表示当时状态；当前入口见[文档导航](../README.md)。

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../maintenance/UPSTREAM.md)，对应关系与恢复材料见[整理记录](../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

**Goal:** Run the existing MSVC build from PowerShell without WSL/Cygwin or automatic downloads.

**Approved scope:** The preceding discussion selected PowerShell orchestration, existing MSBuild/NMake/mhmake rules, native Windows generators, x64 Release first, and no installer. The user has now requested implementation. CMake migration is separate.

**Architecture:** `buildall.ps1` discovers VS2022 and auxiliary tools, validates them before compiling, and runs the existing dependency order. Makefiles use configurable generator paths and a small Python helper for gzip and text filtering. Changes remain in the user's current checkout for review.

- [x] Add behavioral tests for native byte-stream helpers; run failing tests, implement `tools/build_native.py`, rerun tests.
- [x] Add Windows integration tests for `buildall.ps1 -CheckOnly`, including missing explicit tool paths and no build side effects. Implement tool discovery, temporary environment setup/restoration, exit-code propagation and staged builds.
- [x] Replace hardcoded generator paths in batch files and Mesa recipes; quote Python paths. Replace Unix-only commands in the active mhmake rules using native commands or the tested helper.
- [x] Validate native lexer/parser generation and compile the mhmake build tool using the new entry point. Exercise representative makefile generation recipes; distinguish script validation from a full server build.
- [x] Update `HOW_TO_BUILD.txt` and README with prerequisites, overrides, check-only and build commands. Review the complete diff and rerun relevant tests.

Validation commands: `python -B -m unittest discover -s tools/tests -v`, `powershell -NoProfile -File buildall.ps1 -CheckOnly`, `powershell -NoProfile -File buildall.ps1 -Stage BuildTool -Jobs 8`, and `git diff --check`. No dependency installers or network fetches are invoked.

## Validation results (2026-09-09)

- Native x64 Release FreeType, OpenSSL and pthreads builds succeeded.
- `buildall.ps1 -Stage BuildTool -Jobs 8` and `-Stage Server -Jobs 8` completed with exit code 0. Server output includes vcxsrv.exe, Mesa DLLs, utilities, fonts and core keyboard data.
- 21 unittest checks passed with VCXSRV_TEST_LOCAL_TOOLS=1, including real mhmake redirection/pipes, tool paths containing spaces, failure propagation, environment restoration, XKB/atom generation, and portable runtime staging.
- Windows PowerShell 5.1 and PowerShell 7 check-only validation passed.
- 4,374 generated gzip font/encoding files decompressed successfully; all compressed PCF files had valid signatures.
- Read-only review found no remaining blockers in the changed scripts. Case-aware recipe scanning covered the capitalized Terminus Makefile as well as lowercase makefiles.
- The startup follow-up added portable runtime staging using the existing NSIS file list. The x64 Release server starts with a system-only PATH and accepts an authenticated local TCP connection from xwininfo. All 35 packaged PE files have their imported DLLs available.
- No downloads or dependency installations were performed. Debug/Win32, installer packaging and broader application/GL compatibility remain unverified.
