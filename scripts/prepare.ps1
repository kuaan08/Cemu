# Prepare source trees for Xbox One V1. Run on Windows in PowerShell.
param([string]$Workspace = (Join-Path (Get-Location) 'CemuXboxOneWorkspace'))
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
$Workspace = (Resolve-Path $Workspace).Path
function Ensure-Checkout($name, $url, $branch, $commit) {
    $destination = Join-Path $Workspace $name
    if (!(Test-Path $destination)) {
        git clone --branch $branch --recurse-submodules $url $destination
        if ($LASTEXITCODE -ne 0) { throw "git clone failed: $name" }
        Push-Location $destination
        try {
            git checkout --detach $commit
            if ($LASTEXITCODE -ne 0) { throw "Unable to check out pinned revision: $commit" }
            git submodule update --init --recursive
            if ($LASTEXITCODE -ne 0) { throw "Submodule checkout failed: $name" }
        } finally { Pop-Location }
    } else {
        Write-Host "Keeping existing checkout: $destination"
        Push-Location $destination
        try {
            $actual = (git rev-parse HEAD).Trim()
            if ($LASTEXITCODE -ne 0) { throw "Not a valid Git repository: $destination" }
            if ($actual -ne $commit) {
                Write-Warning "$name checkout differs from pinned revision $commit; patch compatibility is not guaranteed."
            }
        } finally { Pop-Location }
    }
}
Ensure-Checkout 'Cemu' 'https://github.com/rodrigoandrigo/Cemu.git' 'build-msvc-d3d11' 'c70bca6f94c94dc7fc8e5bdda5e55d85c500f371'
Ensure-Checkout 'Cemu-UWP-Host' 'https://github.com/rodrigoandrigo/Cemu-UWP-Host.git' 'main' '7dbfb6aa8716593cf7caed3cbcd39b07aee58c2e'
Ensure-Checkout 'SDL3-uwp' 'https://github.com/rodrigoandrigo/SDL3_UWP.git' 'main' '37ee4ec4f4427e45dab91d1b40a5d075cb7ae255'
python (Join-Path $root 'patches/apply_v1.py') --host (Join-Path $Workspace 'Cemu-UWP-Host')
if ($LASTEXITCODE -ne 0) { throw 'V1 patch failed' }
Write-Host "Xbox One V1 source prepared under $Workspace."