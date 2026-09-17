<#
.SYNOPSIS
Install a pinned Inno Setup 7 for CI and expose ISCC.exe on PATH.

The version and SHA256 are pinned together; update both when upgrading.
Hash verified against the asset published on
https://github.com/jrsoftware/issrc/releases/tag/is-7_1_0
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Version = '7.1.0'
$Sha256 = '0362a383ed217d4c4239b5933866dd96d3eb2102737da92f80f6057a4b40df2f'
$Url = "https://github.com/jrsoftware/issrc/releases/download/is-7_1_0/innosetup-$Version-x64.exe"
$InstallDir = 'C:\InnoSetup7'

$installer = Join-Path $env:TEMP "innosetup-$Version-x64.exe"
Write-Host "Downloading $Url"
curl.exe -sSL --retry 3 -o $installer $Url
if ($LASTEXITCODE -ne 0) { throw "Download failed: $Url" }

$actual = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $Sha256) {
    throw "SHA256 mismatch for $installer : expected $Sha256, got $actual"
}

Write-Host "Installing Inno Setup $Version to $InstallDir"
$arguments = '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/CURRENTUSER', "/DIR=$InstallDir"
$process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Inno Setup installer exited with $($process.ExitCode)" }

$iscc = Join-Path $InstallDir 'ISCC.exe'
if (-not (Test-Path -LiteralPath $iscc -PathType Leaf)) { throw "ISCC.exe missing after install: $iscc" }
Add-Content -Path $env:GITHUB_PATH -Value $InstallDir
Write-Host "ISCC.exe: $iscc"
