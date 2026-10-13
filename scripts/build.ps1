# Compile only on a Windows x64 PC with Visual Studio UWP tools.
param(
    [string]$Workspace = (Join-Path (Get-Location) 'CemuXboxOneWorkspace'),
    [string]$Generator = 'Visual Studio 18 2026',
    [string]$MSBuild = 'C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe'
)
$ErrorActionPreference = 'Stop'
$Workspace = (Resolve-Path $Workspace).Path
$cemu = Join-Path $Workspace 'Cemu'
$hostDir = Join-Path $Workspace 'Cemu-UWP-Host'
$sdl = Join-Path $Workspace 'SDL3-uwp'
foreach ($dir in @($cemu, $hostDir, $sdl)) {
    if (!(Test-Path $dir)) { throw "Missing $dir; run scripts/prepare.ps1 first." }
}
if (!(Test-Path $MSBuild)) {
    throw "MSBuild missing: $MSBuild. Provide your Visual Studio MSBuild.exe with -MSBuild."
}
Push-Location $cemu
try {
    cmake -S . -B build-msvc-d3d11 -G $Generator -A x64 -DCEMU_UWP=ON -DENABLE_D3D11=ON -DENABLE_D3D12=ON "-DSDL3_UWP_SOURCE_DIR=$sdl"
    if ($LASTEXITCODE -ne 0) { throw 'Cemu CMake configuration failed.' }
    cmake --build build-msvc-d3d11 --config Release --target CemuBin --parallel
    if ($LASTEXITCODE -ne 0) { throw 'Cemu runtime compilation failed.' }
} finally { Pop-Location }
Push-Location $hostDir
try {
    & $MSBuild '.\Cemu-UWP-Host.vcxproj' /restore /m /p:Configuration=Release /p:Platform=x64 /p:AppxBundle=Always
    if ($LASTEXITCODE -ne 0) { throw 'UWP host compilation failed.' }
} finally { Pop-Location }
Write-Host 'Inspect Cemu-UWP-Host/AppPackages for a signed x64 package. Compile result and hardware support must be tested.'