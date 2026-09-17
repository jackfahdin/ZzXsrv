<#
.SYNOPSIS
Install the pinned native code generators the build needs but the
windows-2025 runner image does not ship: NASM, WinFlexBison and gperf.

Versions and SHA256 hashes are pinned together; update both when upgrading.
The gperf binary is the GnuWin32 3.0.1 build, byte-identical to the
gperf.exe bundled with Qt 5.15.2 sources that local builds use; it depends
only on KERNEL32/msvcrt, so buildall.ps1's native-tool check accepts it.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ToolsRoot = 'C:\zzxsrv-tools'
$Pinned = @(
    @{
        Name   = 'nasm'
        Url    = 'https://www.nasm.us/pub/nasm/releasebuilds/2.16.03/win64/nasm-2.16.03-win64.zip'
        Sha256 = '3ee4782247bcb874378d02f7eab4e294a84d3d15f3f6ee2de2f47a46aa7226e6'
        BinDir = 'nasm-2.16.03'   # zip ships a top-level folder
    },
    @{
        Name   = 'winflexbison'
        Url    = 'https://github.com/lexxmark/winflexbison/releases/download/v2.5.25/win_flex_bison-2.5.25.zip'
        Sha256 = '8d324b62be33604b2c45ad1dd34ab93d722534448f55a16ca7292de32b6ac135'
        BinDir = ''               # executables at zip root
    },
    @{
        Name   = 'gperf'
        Url    = 'https://sourceforge.net/projects/gnuwin32/files/gperf/3.0.1/gperf-3.0.1-bin.zip/download'
        Sha256 = '413d9f5562c39c2fcac1e48b3e2155838680a0aec1ddcb95b23cb2f092962dcc'
        BinDir = 'bin'            # gperf.exe under bin/
    }
)

$null = New-Item -ItemType Directory -Path $ToolsRoot -Force
foreach ($tool in $Pinned) {
    $archive = Join-Path $env:TEMP ($tool.Name + '.zip')
    Write-Host "Downloading $($tool.Url)"
    curl.exe -sSL --retry 3 -o $archive $tool.Url
    if ($LASTEXITCODE -ne 0) { throw "Download failed: $($tool.Url)" }
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $tool.Sha256) {
        throw "SHA256 mismatch for $($tool.Name): expected $($tool.Sha256), got $actual"
    }
    $destination = Join-Path $ToolsRoot $tool.Name
    Expand-Archive -LiteralPath $archive -DestinationPath $destination -Force
    $binDir = if ($tool.BinDir) { Join-Path $destination $tool.BinDir } else { $destination }
    if (-not (Get-ChildItem -LiteralPath $binDir -Filter '*.exe' -File)) {
        throw "No executables found under $binDir after extracting $($tool.Name)"
    }
    Add-Content -Path $env:GITHUB_PATH -Value $binDir
    Write-Host "$($tool.Name): $binDir"
}
