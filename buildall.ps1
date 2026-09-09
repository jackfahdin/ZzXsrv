<#
.SYNOPSIS
Build VcXsrv with native Windows tools. Does not download or install anything.
.EXAMPLE
.\buildall.ps1 -CheckOnly
.EXAMPLE
.\buildall.ps1 -Configuration Release -Architecture x64 -Jobs 8
.EXAMPLE
.\buildall.ps1 -WinFlexBisonPath D:\Tools\win_flex_bison -PythonPath D:\Python\python.exe
.EXAMPLE
.\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment.json
#>
[CmdletBinding()]
param(
    [ValidateSet('Release', 'Debug')][string]$Configuration = 'Release',
    [ValidateSet('x64', 'Win32')][string]$Architecture = 'x64',
    [ValidateSet('All', 'Dependencies', 'BuildTool', 'Server', 'Portable')][string]$Stage = 'All',
    [ValidateRange(1, 128)][int]$Jobs = [Math]::Min(16, [Environment]::ProcessorCount),
    [switch]$CheckOnly,
    [string]$VisualStudioPath,
    [string]$PythonPath,
    [string]$WinFlexBisonPath,
    [string]$PerlPath,
    [string]$NasmPath,
    [string]$GperfPath,
    [string]$JomPath,
    [string]$EnvironmentReport
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# External tools use their exit code; stderr alone is not a failure (PowerShell 7).
$PSNativeCommandUseErrorActionPreference = $false
$repoRoot = $PSScriptRoot
if ($repoRoot -match '\s') {
    throw 'The existing mhmake rules require a source checkout path without spaces.'
}
$environmentReportPath = if ($EnvironmentReport) {
    $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($EnvironmentReport)
} else { $null }

function Find-BuildTool {
    param([string]$Name, [string]$ExplicitPath, [string[]]$Candidates = @(), [switch]$Optional)
    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            throw "Missing $Name at the specified path: $ExplicitPath"
        }
        return (Get-Item -LiteralPath $ExplicitPath).FullName
    }
    $command = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command -and $command.Source -notmatch '\\WindowsApps\\') { return $command.Source }
    foreach ($candidate in $Candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            return (Get-Item -LiteralPath $candidate).FullName
        }
    }
    if (-not $Optional) { throw "Cannot find $Name. Install it separately or provide its path using the script parameters." }
}

function Invoke-BuildCommand {
    param([string]$File, [string[]]$Arguments = @())
    Write-Host ('> "{0}" {1}' -f $File, ($Arguments -join ' '))
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$File failed with exit code $LASTEXITCODE." }
}

function Assert-NativeTool {
    param([string]$File)
    $imports = & dumpbin.exe /nologo /dependents $File 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect Windows executable: $File" }
    if (($imports -join "`n") -match '(?i)cygwin1\.dll|msys-2\.0\.dll') {
        throw "A native Windows version is required; this tool depends on Cygwin/MSYS: $File"
    }
}

function In-BuildDirectory {
    param([string]$Directory, [scriptblock]$Action)
    Push-Location -LiteralPath $Directory
    try { & $Action } finally { Pop-Location }
}

function Get-ToolVersion {
    param([string]$Path)
    if (-not $Path) { return $null }
    try {
        $version = (Get-Item -LiteralPath $Path -ErrorAction Stop).VersionInfo.ProductVersion
        if ($version) { return $version.Trim() }
    } catch {
        return $null
    }
    return $null
}

function New-ToolReportEntry {
    param([string]$Path, [AllowNull()][object]$Version = $null)
    [ordered]@{
        path = if ($Path) { [System.IO.Path]::GetFullPath($Path) } else { $null }
        version = if ($null -eq $Version -or [string]::IsNullOrWhiteSpace([string]$Version)) {
            $null
        } else { [string]$Version }
    }
}

function Write-EnvironmentReport {
    param(
        [string]$Path,
        [string]$Python,
        [string]$Cl,
        [string]$MSBuild,
        [string]$Dumpbin,
        [string]$Flex,
        [string]$Bison,
        [AllowNull()][string]$Perl = $null,
        [AllowNull()][string]$Nasm = $null,
        [AllowNull()][string]$Gperf = $null,
        [AllowNull()][string]$Jom = $null
    )

    $pythonMetadataText = & $Python '-B' '-c' "import importlib.metadata as m, json, platform; print(json.dumps({'version': platform.python_version(), 'packages': {name: m.version(name) for name in ('lxml', 'mako', 'PyYAML')}}))" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Cannot query package metadata from the selected Python: $Python" }
    try {
        $pythonMetadata = ($pythonMetadataText -join "`n") | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "Selected Python returned invalid package metadata: $Python"
    }

    $git = Find-BuildTool 'git.exe'
    $sourceCommitText = & $git '-C' $repoRoot 'rev-parse' 'HEAD' 2>&1
    if ($LASTEXITCODE -ne 0) { throw 'Cannot determine the source commit for the environment report.' }
    $sourceCommit = ([string]($sourceCommitText | Select-Object -First 1)).Trim()
    if ($sourceCommit -notmatch '^[0-9a-fA-F]{40}$') { throw 'Git returned an invalid source commit for the environment report.' }

    $tools = [ordered]@{}
    $tools['python'] = New-ToolReportEntry $Python ([string]$pythonMetadata.version)
    $tools['cl'] = New-ToolReportEntry $Cl (Get-ToolVersion $Cl)
    $tools['msbuild'] = New-ToolReportEntry $MSBuild (Get-ToolVersion $MSBuild)
    $tools['dumpbin'] = New-ToolReportEntry $Dumpbin (Get-ToolVersion $Dumpbin)
    $tools['flex'] = New-ToolReportEntry $Flex (Get-ToolVersion $Flex)
    $tools['bison'] = New-ToolReportEntry $Bison (Get-ToolVersion $Bison)
    if ($Perl) { $tools['perl'] = New-ToolReportEntry $Perl (Get-ToolVersion $Perl) }
    if ($Nasm) { $tools['nasm'] = New-ToolReportEntry $Nasm (Get-ToolVersion $Nasm) }
    if ($Gperf) { $tools['gperf'] = New-ToolReportEntry $Gperf (Get-ToolVersion $Gperf) }
    if ($Jom) { $tools['jom'] = New-ToolReportEntry $Jom (Get-ToolVersion $Jom) }
    $tools['msvc'] = New-ToolReportEntry $env:VCToolsInstallDir $env:VCToolsVersion
    $sdkVersion = if ($env:WindowsSDKVersion) { $env:WindowsSDKVersion.TrimEnd('\') } else { $null }
    $tools['sdk'] = New-ToolReportEntry $env:WindowsSdkDir $sdkVersion

    $report = [ordered]@{
        schema_version = 1
        source_commit = $sourceCommit.ToLowerInvariant()
        target = [ordered]@{
            architecture = $Architecture
            configuration = $Configuration
        }
        host = [ordered]@{
            name = $env:COMPUTERNAME
            windows_version = [Environment]::OSVersion.VersionString
            powershell_version = $PSVersionTable.PSVersion.ToString()
        }
        tools = $tools
        python_packages = [ordered]@{
            lxml = [string]$pythonMetadata.packages.lxml
            mako = [string]$pythonMetadata.packages.mako
            PyYAML = [string]$pythonMetadata.packages.PyYAML
        }
    }

    $json = $report | ConvertTo-Json -Depth 6
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        $null = New-Item -ItemType Directory -Path $parent -Force
    }
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false))
    Write-Host "Environment report: $Path"
}

# Environment changes are scoped to this invocation, including calls from an
# existing Developer PowerShell. Never change the user's persistent PATH.
$savedEnvironment = @{}
Get-ChildItem Env: | ForEach-Object { $savedEnvironment[$_.Name] = $_.Value }
try {
    if (-not $VisualStudioPath) {
        $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
        if (-not (Test-Path -LiteralPath $vswhere)) { throw 'VS2022 Installer/vswhere was not found. Specify -VisualStudioPath.' }
        $VisualStudioPath = & $vswhere -latest -products '*' -version '[17.0,18.0)' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        if (-not $VisualStudioPath) { throw 'VS2022 with the C++ x86/x64 tools is required.' }
    }
    $vcvars = Join-Path $VisualStudioPath 'VC\Auxiliary\Build\vcvarsall.bat'
    if (-not (Test-Path -LiteralPath $vcvars)) { throw "Missing Visual Studio environment script: $vcvars" }
    $vcArchitecture = if ($Architecture -eq 'x64') { 'amd64' } else { 'amd64_x86' }
    # Capture (do not print) the child environment so paths on any drive work.
    Push-Location -LiteralPath (Split-Path $vcvars)
    try {
        $vcEnvironment = & $env:ComSpec /d /c "call vcvarsall.bat $vcArchitecture >nul && set"
        if ($LASTEXITCODE -ne 0) { throw 'Visual Studio environment initialization failed.' }
        foreach ($line in $vcEnvironment) {
            if ($line -match '^([^=]+)=(.*)$') {
                if (-not $savedEnvironment.ContainsKey($Matches[1]) -or $savedEnvironment[$Matches[1]] -cne $Matches[2]) {
                    [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
                }
            }
        }
    } finally { Pop-Location }

    $nativeTools = @{}
    foreach ($name in 'cl.exe', 'link.exe', 'lib.exe', 'rc.exe', 'nmake.exe', 'dumpbin.exe') {
        $nativeTools[$name] = Find-BuildTool $name
    }
    $cl = $nativeTools['cl.exe']
    $dumpbin = $nativeTools['dumpbin.exe']
    $msbuild = Find-BuildTool 'MSBuild.exe' -Candidates @((Join-Path $VisualStudioPath 'MSBuild\Current\Bin\MSBuild.exe'))
    $searchRoots = @($env:ProgramFiles, ${env:ProgramFiles(x86)}, (Join-Path $env:LOCALAPPDATA 'Programs'))
    foreach ($drive in Get-PSDrive -PSProvider FileSystem) {
        if ($drive.Root -match '^[A-Za-z]:\\$') {
            $searchRoots += Join-Path $drive.Root 'SoftWare'
            $searchRoots += Join-Path $drive.Root 'Tools'
        }
    }
    $searchRoots = @($searchRoots | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique)
    $python = Find-BuildTool 'python.exe' $PythonPath
    Assert-NativeTool $python
    Invoke-BuildCommand $python @('-B', '-c', "import sys; assert sys.platform == 'win32', 'Use Windows Python'; assert sys.version_info >= (3,11), 'Python 3.11 or newer is required'; from lxml import etree; from mako.template import Template; import yaml; etree.fromstring(b'<ok/>'); Template('ok').render(); print('Python dependencies OK:', sys.executable)")

    $flexCandidates = @()
    $bisonCandidates = @()
    foreach ($root in $searchRoots) {
        foreach ($dir in @(Get-ChildItem -Path (Join-Path $root '*flex*bison*') -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending)) {
            $flexCandidates += Join-Path $dir.FullName 'win_flex.exe'
            $bisonCandidates += Join-Path $dir.FullName 'win_bison.exe'
        }
    }
    $flexExplicit = if ($WinFlexBisonPath) { Join-Path $WinFlexBisonPath 'win_flex.exe' } else { '' }
    $bisonExplicit = if ($WinFlexBisonPath) { Join-Path $WinFlexBisonPath 'win_bison.exe' } else { '' }
    $flex = Find-BuildTool 'win_flex.exe' $flexExplicit $flexCandidates
    $bison = Find-BuildTool 'win_bison.exe' $bisonExplicit $bisonCandidates
    foreach ($tool in $flex, $bison) {
        Assert-NativeTool $tool
        Invoke-BuildCommand $tool @('--version')
    }
    $env:PYTHON3 = $python
    $env:WIN_FLEX = $flex
    $env:WIN_BISON = $bison
    $env:MHMAKECONF = $repoRoot
    $env:IS64 = if ($Architecture -eq 'x64') { '1' } else { '0' }
    $env:CFLAGS = '-FS'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    # Generated code and data use UTF-8, independently of Windows' ANSI locale.
    $env:PYTHONUTF8 = '1'
    $env:LC_ALL = 'C'
    # Legacy makefiles also read DEBUG from the environment. A stale value
    # must not mix Debug objects with Release dependencies (or vice versa).
    Remove-Item Env:DEBUG -ErrorAction SilentlyContinue

    if ($Stage -ne 'BuildTool') {
        $perl = Find-BuildTool 'perl.exe' $PerlPath
        $nasm = Find-BuildTool 'nasm.exe' $NasmPath
        $gperfCandidates = @()
        $jomCandidates = @()
        foreach ($root in $searchRoots) {
            $gperfCandidates += @(Get-ChildItem -Path (Join-Path $root 'Qt\*\Src\gnuwin32\bin\gperf.exe') -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
            $jomCandidates += Join-Path $root 'Qt\Tools\QtCreator\bin\jom\jom.exe'
        }
        $gperf = Find-BuildTool 'gperf.exe' $GperfPath $gperfCandidates
        $jom = Find-BuildTool 'jom.exe' $JomPath $jomCandidates -Optional
        foreach ($tool in @($perl, $nasm, $gperf) + @($jom | Where-Object { $_ })) { Assert-NativeTool $tool }
        $env:GPERF = $gperf
        # Compiler tools stay first so MinGW tools shipped with Perl cannot
        # shadow MSVC's linker. Generator paths are also passed explicitly.
        $compilerDirectory = Split-Path (Find-BuildTool 'cl.exe')
        $env:PATH = $compilerDirectory + ';' + ((@($nasm, $perl, $gperf) | ForEach-Object { Split-Path $_ } | Select-Object -Unique) -join ';') + ';' + $env:PATH
        $env:PERL = $perl
        Write-Host "Perl: $perl`nNASM: $nasm`nGPERF: $gperf"
        if ($jom) { Write-Host "OpenSSL make: $jom" } else { Write-Host 'OpenSSL make: NMake (serial)' }
    }
    Write-Host "Visual Studio: $VisualStudioPath`nTarget: $Architecture $Configuration; stage: $Stage"
    if ($environmentReportPath) {
        $reportArguments = @{
            Path = $environmentReportPath
            Python = $python
            Cl = $cl
            MSBuild = $msbuild
            Dumpbin = $dumpbin
            Flex = $flex
            Bison = $bison
        }
        if ($Stage -ne 'BuildTool') {
            $reportArguments['Perl'] = $perl
            $reportArguments['Nasm'] = $nasm
            $reportArguments['Gperf'] = $gperf
            if ($jom) { $reportArguments['Jom'] = $jom }
        }
        Write-EnvironmentReport @reportArguments
    }
    if ($CheckOnly) {
        Write-Host 'Environment check passed. No build commands were executed.'
        return
    }

    $suffix = if ($Architecture -eq 'x64') { '64' } else { '32' }
    $mhmakeDirectory = if ($Architecture -eq 'x64') { 'Release64' } else { 'Release' }
    $mhmake = Join-Path $repoRoot "tools\mhmake\$mhmakeDirectory\mhmake.exe"
    In-BuildDirectory $repoRoot {
        if ($Stage -in @('All', 'Dependencies')) {
            Invoke-BuildCommand $msbuild @('freetype\MSBuild.sln', '-t:Build', "-p:Configuration=$Configuration", "-p:Platform=$Architecture", "-m:$Jobs", '-nologo', '-v:minimal')
            $opensslDirectory = Join-Path $repoRoot ("openssl\" + $Configuration.ToLowerInvariant() + $suffix)
            $null = New-Item -ItemType Directory -Path $opensslDirectory -Force
            In-BuildDirectory $opensslDirectory {
                $opensslTarget = if ($Architecture -eq 'x64') { 'VC-WIN64A' } else { 'VC-WIN32' }
                Invoke-BuildCommand $perl @('..\Configure', $opensslTarget, ('--' + $Configuration.ToLowerInvariant()))
                # OpenSSL's tools/tests share app.pdb; parallel builds can fail
                # with C1041 even with -FS. Keep only this stage serial.
                if ($jom) { Invoke-BuildCommand $jom @('/J1') }
                else { Invoke-BuildCommand 'nmake.exe' @('/nologo') }
            }
            In-BuildDirectory (Join-Path $repoRoot 'pthreads') {
                $pthreadTarget = if ($Configuration -eq 'Debug') { 'VC-static-debug' } else { 'VC-static' }
                Invoke-BuildCommand 'nmake.exe' @('/nologo', $pthreadTarget)
            }
        }
        if ($Stage -in @('All', 'Dependencies', 'BuildTool')) {
            # mhmake itself always uses Release, including Debug server builds.
            Invoke-BuildCommand $msbuild @('tools\mhmake\mhmakevc10.sln', '-t:Build', '-p:Configuration=Release', "-p:Platform=$Architecture", "-m:$Jobs", '-nologo', '-v:minimal')
        }
        if ($Stage -in @('All', 'Server')) {
            if (-not (Test-Path -LiteralPath $mhmake)) { throw "Build mhmake/dependencies first: $mhmake" }
            $buildArguments = @("-P$Jobs", '-C', 'xorg-server', 'MAKESERVER=1')
            $buildArguments += if ($Configuration -eq 'Debug') { 'DEBUG=1' } else { 'DEBUG=0' }
            Invoke-BuildCommand $mhmake $buildArguments
        }
        if ($Stage -in @('All', 'Server', 'Portable')) {
            $manifestSuffix = if ($Architecture -eq 'x64') { '-64' } else { '' }
            if ($Configuration -eq 'Debug') { $manifestSuffix += '-debug' }
            $crtArchitecture = if ($Architecture -eq 'x64') { 'x64' } else { 'x86' }
            $crtRelative = if ($Configuration -eq 'Debug') {
                "debug_nonredist\$crtArchitecture\Microsoft.VC143.DebugCRT"
            } else { "$crtArchitecture\Microsoft.VC143.CRT" }
            $crtDirectory = Join-Path $env:VCToolsRedistDir $crtRelative
            $portableDirectory = Join-Path $repoRoot "dist\$Architecture\$Configuration"
            Invoke-BuildCommand $python @('-B', 'tools\package_portable.py', '--manifest', "xorg-server\installer\vcxsrv$manifestSuffix.nsi", '--crt-directory', $crtDirectory, '--output', $portableDirectory)
        }
    }
    Write-Host "Completed stage: $Stage. Installer packaging is a separate step."
} finally {
    foreach ($entry in @(Get-ChildItem Env:)) {
        if (-not $savedEnvironment.ContainsKey($entry.Name)) {
            Remove-Item -LiteralPath ("Env:" + $entry.Name)
        }
    }
    $currentEnvironment = @{}
    Get-ChildItem Env: | ForEach-Object { $currentEnvironment[$_.Name] = $_.Value }
    foreach ($name in $savedEnvironment.Keys) {
        if (-not $currentEnvironment.ContainsKey($name) -or $currentEnvironment[$name] -cne $savedEnvironment[$name]) {
            [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
        }
    }
}
