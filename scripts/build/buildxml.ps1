<# Build the pinned native libiconv and libxml2 sources without downloading. #>
[CmdletBinding()]
param(
    [ValidateSet('Release', 'Debug')][string]$Configuration = 'Release',
    [ValidateSet('x64', 'Win32')][string]$Architecture = 'x64',
    [ValidateRange(1, 128)][int]$Jobs = [Math]::Min(16, [Environment]::ProcessorCount),
    [string]$CMakePath,
    [switch]$CheckOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$iconvRoot = Join-Path $repoRoot 'third_party\libiconv'
$xmlRoot = Join-Path $repoRoot 'third_party\libxml2'
$iconvOutput = Join-Path $iconvRoot "build\$Architecture\$Configuration"
$xmlOutput = Join-Path $xmlRoot "build\$Architecture\$Configuration"
$objSuffix = if ($Architecture -eq 'x64') { '64' } else { '' }
$objConfig = $Configuration.ToLowerInvariant()
$zlibLibrary = Join-Path $repoRoot "third_party\zlib\obj$objSuffix\$objConfig\zlib1.lib"
$cmakeArchitecture = if ($Architecture -eq 'x64') { 'x64' } else { 'Win32' }
$configurationUpper = $Configuration.ToUpperInvariant()

if (-not $CMakePath) {
    $visualStudioPath = $env:VSINSTALLDIR
    if (-not $visualStudioPath) {
        $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
        if (Test-Path -LiteralPath $vswhere -PathType Leaf) {
            $visualStudioPath = & $vswhere -latest -products '*' -version '[17.0,18.0)' `
                -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        }
    }
    if ($visualStudioPath) {
        $bundled = Join-Path $visualStudioPath 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
        if (Test-Path -LiteralPath $bundled -PathType Leaf) { $CMakePath = $bundled }
    }
    if (-not $CMakePath) {
        $command = Get-Command cmake.exe -CommandType Application -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($command) { $CMakePath = $command.Source }
    }
}
if (-not $CMakePath -or -not (Test-Path -LiteralPath $CMakePath -PathType Leaf)) {
    throw 'Cannot find cmake.exe. Install it separately or provide -CMakePath.'
}
$CMakePath = (Get-Item -LiteralPath $CMakePath).FullName

$features = [ordered]@{
    iconv = $true
    output = $true
    push = $true
    sax1 = $true
    threads = $true
    tree = $true
    zlib = $true
}
$iconvBinary = Join-Path $iconvOutput 'cmake'
$iconvConfigure = @('-S', $iconvRoot, '-B', $iconvBinary, '-G', 'Visual Studio 17 2022',
    '-A', $cmakeArchitecture,
    "-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_$configurationUpper=$iconvOutput",
    "-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_$configurationUpper=$iconvOutput",
    "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_$configurationUpper=$iconvOutput")
$iconvBuild = @('--build', $iconvBinary, '--config', $Configuration, '--parallel', "$Jobs")
$xmlBinary = Join-Path $xmlOutput 'cmake-wrapper'
$xmlConfigure = @('-S', $xmlRoot, '-B', $xmlBinary,
    '-G', 'Visual Studio 17 2022', '-A', $cmakeArchitecture,
    '-DBUILD_SHARED_LIBS=ON', '-DLIBXML2_WITH_ICONV=ON', '-DLIBXML2_WITH_ZLIB=ON',
    '-DLIBXML2_WITH_TESTS=OFF', '-DLIBXML2_WITH_PYTHON=OFF', '-DLIBXML2_WITH_PROGRAMS=OFF',
    '-DLIBXML2_WITH_OUTPUT=ON', '-DLIBXML2_WITH_PUSH=ON', '-DLIBXML2_WITH_SAX1=ON',
    '-DLIBXML2_WITH_THREADS=ON',
    "-DIconv_INCLUDE_DIR=$(Join-Path $iconvRoot 'source\include')",
    "-DIconv_LIBRARY=$(Join-Path $iconvOutput 'libiconv.lib')",
    "-DZLIB_INCLUDE_DIR=$(Join-Path $repoRoot 'third_party\zlib')",
    "-DZLIB_LIBRARY=$zlibLibrary",
    "-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_$configurationUpper=$xmlOutput",
    "-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_$configurationUpper=$xmlOutput",
    "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_$configurationUpper=$xmlOutput")
$xmlBuild = @('--build', $xmlBinary, '--config', $Configuration, '--parallel', "$Jobs")
$plan = [ordered]@{
    target = [ordered]@{ architecture = $Architecture; configuration = $Configuration }
    cmake = $CMakePath
    zlib_library = $zlibLibrary
    iconv = [ordered]@{
        source = Join-Path $iconvRoot 'source'
        outputs = @((Join-Path $iconvOutput 'libiconv.dll'), (Join-Path $iconvOutput 'libiconv.lib'))
        configure = $iconvConfigure
        build = $iconvBuild
    }
    libxml2 = [ordered]@{
        source = Join-Path $xmlRoot 'source'
        outputs = @((Join-Path $xmlOutput 'libxml2.dll'), (Join-Path $xmlOutput 'libxml2.lib'))
        include = Join-Path $xmlOutput 'include'
        features = $features
        configure = $xmlConfigure
        build = $xmlBuild
    }
}
if ($CheckOnly) {
    $plan | ConvertTo-Json -Depth 5 -Compress
    return
}

foreach ($required in @((Join-Path $iconvRoot 'source\lib\iconv.c'),
                         (Join-Path $xmlRoot 'source\CMakeLists.txt'), $zlibLibrary)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing build input: $required" }
}

function Invoke-CMake {
    param([string[]]$Arguments)
    Write-Host ('> "{0}" {1}' -f $CMakePath, ($Arguments -join ' '))
    & $CMakePath @Arguments
    if ($LASTEXITCODE -ne 0) { throw "cmake.exe failed with exit code $LASTEXITCODE." }
}

Invoke-CMake $iconvConfigure
Invoke-CMake $iconvBuild
Invoke-CMake $xmlConfigure
Invoke-CMake $xmlBuild

$includeOutput = Join-Path $xmlOutput 'include'
$libxmlIncludeOutput = Join-Path $includeOutput 'libxml'
$null = New-Item -ItemType Directory -Path $libxmlIncludeOutput -Force
Copy-Item -Path (Join-Path $xmlRoot 'source\include\libxml\*') -Destination $libxmlIncludeOutput -Recurse -Force
Copy-Item -LiteralPath (Join-Path $xmlBinary 'upstream\libxml\xmlversion.h') -Destination (Join-Path $libxmlIncludeOutput 'xmlversion.h') -Force

foreach ($output in @($plan.iconv.outputs + $plan.libxml2.outputs)) {
    if (-not (Test-Path -LiteralPath $output -PathType Leaf)) { throw "Build did not produce: $output" }
}
Write-Host "Built native XML dependencies for $Architecture $Configuration."
