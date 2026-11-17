$projectRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $projectRoot "data\facebox.db"
$dstDir = Join-Path $projectRoot "dist\FaceBox\data"
$dst = Join-Path $dstDir "facebox.db"

if (-not (Test-Path $dstDir)) {
    New-Item -ItemType Directory -Path $dstDir | Out-Null
    Write-Host "Created dir: $dstDir"
}

if (Test-Path $src) {
    Copy-Item $src $dst -Force
    $size = (Get-Item $dst).Length
    Write-Host "DB copied: $dst ($size bytes)"
} else {
    Write-Host "Source DB not found at $src - fresh DB will be created on first run"
}

