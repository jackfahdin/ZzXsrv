# ZzXsrv

Windows X-server based on the xorg git sources (like xming or cygwin's xwin), compiled with Visual Studio 2022.

This fork starts from marchaesen/vcxsrv commit
`d0a1eaf7ee15fcdf4f683388a88fec49078e6408`. Original history is archived locally;
copyright and license materials remain intact. See [FORK.md](FORK.md) for provenance
and the old-to-new commit mapping.

Current work and remaining items: [plan status](docs/PLAN_STATUS.md).
Manual application coverage: [compatibility record](docs/COMPATIBILITY.md).

Repository: [jackfahdin/ZzXsrv](https://github.com/jackfahdin/ZzXsrv).

`master` is the single long-lived branch and keeps a linear history. Dependency
origins, pinned commits/versions and inherited source URLs are recorded in
[dependency sources](docs/DEPENDENCY_SOURCES.md). There is no upstream source
branch. See [maintenance rules](docs/UPSTREAM.md) for future updates.

For a native Windows build without WSL or Cygwin, run `./buildall.ps1 -CheckOnly`
from PowerShell, then `./buildall.ps1 -Jobs 8`. See [HOW_TO_BUILD.txt](HOW_TO_BUILD.txt)
for prerequisites, tool path overrides and build stages. Tools are never downloaded
automatically. The older `buildall.sh` entry point assumes a WSL terminal and a
Windows folder (a case insensitive filesystem is needed).

After building, launch `dist/x64/Release/xlaunch.exe` (startup wizard) or
`dist/x64/Release/vcxsrv.exe`. Keep the complete runtime folder together.
Use `./buildall.ps1 -Stage Portable` to assemble it from existing build outputs.

Local maintenance direction, verification criteria and the next implementation
plan are documented in [docs/MAINTENANCE.md](docs/MAINTENANCE.md) (Chinese).
