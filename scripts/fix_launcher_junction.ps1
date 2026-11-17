# Script tao junction C:\FaceBoxApp -> dist\FaceBox (ASCII path)
# va tao VBS launcher su dung path ASCII

$junctionPath = 'C:\FaceBoxApp'
$distPath = 'D:\Project Antigravity IDE\Du an FaceBox\FaceBox\dist\FaceBox'

# Tim dist path that su (co Unicode)
$unicodeDist = Join-Path (Split-Path -Parent $PSScriptRoot) 'dist\FaceBox'
Write-Host "Dist path: $unicodeDist"
Write-Host "EXE exists: $(Test-Path (Join-Path $unicodeDist 'FaceBox.exe'))"

# Tao junction neu chua co
if (Test-Path $junctionPath) {
    Write-Host "Junction already exists at $junctionPath"
} else {
    cmd /c mklink /J $junctionPath $unicodeDist 2>&1
    Start-Sleep -Milliseconds 500
}

$junctionExe = Join-Path $junctionPath 'FaceBox.exe'
Write-Host "Junction EXE: $junctionExe"
Write-Host "Junction EXE exists: $(Test-Path $junctionExe)"

# Tao VBS voi ASCII path
$desktop = [System.Environment]::GetFolderPath('Desktop')
$vbsPath = Join-Path $desktop 'FaceBox.vbs'

$vbsContent = @"
Dim objShell
Set objShell = CreateObject("Shell.Application")

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

Dim exePath
exePath = "C:\FaceBoxApp\FaceBox.exe"

If Not fso.FileExists(exePath) Then
    MsgBox "Khong tim thay FaceBox.exe!" & Chr(13) & Chr(10) & exePath, 16, "FaceBox - Loi khoi dong"
Else
    objShell.ShellExecute exePath, "", "C:\FaceBoxApp", "open", 1
End If

Set fso = Nothing
Set objShell = Nothing
"@

[System.IO.File]::WriteAllText($vbsPath, $vbsContent, [System.Text.Encoding]::Default)
Write-Host "VBS saved: $vbsPath"
Write-Host "VBS size: $((Get-Item $vbsPath).Length) bytes"

# Hien thi noi dung
Write-Host "--- VBS content ---"
Get-Content $vbsPath

