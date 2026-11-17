# FaceBox — Script chuẩn bị Database cho bản phát hành
# Mặc định: Tạo database sạch 100% dựa trên schema.sql và khởi tạo 30 ngăn tủ mặc định.
# Tuyệt đối không sao chép dữ liệu sinh trắc học hoặc tài khoản cá nhân vào bản release.

param(
    [switch]$DevCopy = $false
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$distDataDir = Join-Path $projectRoot "dist\FaceBox\data"
$dst = Join-Path $distDataDir "facebox.db"

if (-not (Test-Path $distDataDir)) {
    New-Item -ItemType Directory -Path $distDataDir | Out-Null
    Write-Host "Created dir: $distDataDir"
}

if ($DevCopy) {
    # Chỉ dùng cho mục đích kiểm thử nội bộ của lập trình viên
    $src = Join-Path $projectRoot "data\facebox.db"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        $size = (Get-Item $dst).Length
        Write-Host "[DEV ONLY] Copied dev DB to dist: $dst ($size bytes)"
    } else {
        Write-Host "Dev DB not found at $src"
    }
} else {
    # Mặc định an toàn cho bản phát hành: Khởi tạo DB sạch
    $initScript = Join-Path $projectRoot "scripts\init_release_db.py"
    Write-Host "Đang tạo cơ sở dữ liệu sạch cho bản phát hành..."
    python $initScript $dst
}
