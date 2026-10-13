# Prepare editable Xbox One source checkouts from the three dedicated branches.
param(
    [string]$Workspace = (Join-Path (Get-Location) 'CemuXboxOneWorkspace'),
    [string]$Repository = 'https://github.com/kuaan08/Cemu.git'
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
$Workspace = (Resolve-Path $Workspace).Path

function Ensure-Checkout([string]$name, [string]$branch) {
    $destination = Join-Path $Workspace $name
    if (!(Test-Path $destination)) {
        git clone --single-branch --branch $branch --recurse-submodules $Repository $destination
        if ($LASTEXITCODE -ne 0) { throw "Clone failed: $name / $branch" }
    } else {
        Push-Location $destination
        try {
            $actual = (git branch --show-current).Trim()
            if ($LASTEXITCODE -ne 0) { throw "Not a valid Git checkout: $destination" }
            if ($actual -ne $branch) {
                throw "$destination is on branch '$actual' instead of '$branch'. Do not overwrite existing changes."
            }
            Write-Host "Keeping local source and edits: $destination ($actual)"
            git submodule update --init --recursive
            if ($LASTEXITCODE -ne 0) { throw "Failed to initialize submodules: $name" }
        } finally { Pop-Location }
    }
}
Ensure-Checkout 'Cemu' 'xbox-one/cemu-core'
Ensure-Checkout 'Cemu-UWP-Host' 'xbox-one/uwp-host'
Ensure-Checkout 'SDL3-uwp' 'xbox-one/sdl3-uwp'

# Supports both a clean imported host and a host branch patched directly:
# the source patcher is idempotent and will not overwrite unrelated edits.
python (Join-Path $root 'patches/apply_v1.py') --host (Join-Path $Workspace 'Cemu-UWP-Host')
if ($LASTEXITCODE -ne 0) { throw 'Xbox One V1 patch failed; inspect existing local edits.' }
Write-Host "Editable Xbox One source trees are available under $Workspace."