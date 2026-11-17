$projectRoot = Split-Path -Parent $PSScriptRoot
$exePath = Join-Path $projectRoot "dist\FaceBox\FaceBox.exe"
$workDir = Join-Path $projectRoot "dist\FaceBox"
$icoPath = Join-Path $projectRoot "dist\FaceBox\_internal\assets\FaceBox.ico"
$shortcutPath = "$env:USERPROFILE\Desktop\FaceBox.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $workDir
$shortcut.IconLocation = "$icoPath,0"
$shortcut.Description = "FaceBox - He Thong Tu Thong Minh & Dinh Danh Sinh Trac Hoc"
$shortcut.Save()

if (Test-Path $shortcutPath) {
    Write-Host "Shortcut created: $shortcutPath"
} else {
    Write-Host "ERROR: Failed to create shortcut"
}

