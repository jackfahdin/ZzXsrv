Windows X-server based on the xorg git sources (like xming or cygwin's xwin), compiled with Visual Studio 2022.

Branches:

- released: contains original sources of all used packages.
- master: contains all necessary changes to be able to compile with Visual Studio. From this branch the binary releases are built.

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
