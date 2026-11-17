Add-Type -AssemblyName System.Runtime.InteropServices

# Get short 8.3 path to avoid Unicode issues with WScript.Shell
function Get-ShortPath($longPath) {
    $sb = New-Object System.Text.StringBuilder 260
    $null = [System.Runtime.InteropServices.Marshal]::PtrToStringAnsi([System.IntPtr]::Zero)
    
    # Use GetShortPathName via kernel32
    Add-Type -MemberDefinition @'
[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
public static extern int GetShortPathName(string lpszLongPath, System.Text.StringBuilder lpszShortPath, int cchBuffer);
'@ -Name NativeMethods -Namespace Win32 -ErrorAction SilentlyContinue
    
    $buffer = New-Object System.Text.StringBuilder 260
    $len = [Win32.NativeMethods]::GetShortPathName($longPath, $buffer, 260)
    if ($len -gt 0) { return $buffer.ToString() }
    return $longPath
}

$exePath    = 'D:\Project Antigravity IDE\Du an FaceBox\FaceBox\dist\FaceBox\FaceBox.exe'
$workDir    = 'D:\Project Antigravity IDE\Du an FaceBox\FaceBox\dist\FaceBox'
$icoPath    = 'D:\Project Antigravity IDE\Du an FaceBox\FaceBox\dist\FaceBox\_internal\assets\FaceBox.ico'
$shortcutPath = "$env:USERPROFILE\Desktop\FaceBox.lnk"

# Use actual Unicode paths directly - try different approach
$longExe  = 'D:\Project Antigravity IDE\Dự án FaceBox\FaceBox\dist\FaceBox\FaceBox.exe'
$longWork = 'D:\Project Antigravity IDE\Dự án FaceBox\FaceBox\dist\FaceBox'
$longIco  = 'D:\Project Antigravity IDE\Dự án FaceBox\FaceBox\dist\FaceBox\_internal\assets\FaceBox.ico'

$shortExe  = Get-ShortPath $longExe
$shortWork = Get-ShortPath $longWork
$shortIco  = Get-ShortPath $longIco

Write-Host "Short exe:  $shortExe"
Write-Host "Short work: $shortWork"
Write-Host "Short ico:  $shortIco"

$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $shortExe
$shortcut.WorkingDirectory = $shortWork
$shortcut.IconLocation = "$shortIco,0"
$shortcut.Description = "FaceBox - He Thong Tu Thong Minh"
$shortcut.Save()

if (Test-Path $shortcutPath) {
    Write-Host "SUCCESS: Shortcut created at $shortcutPath"
} else {
    Write-Host "ERROR: Shortcut not found after save"
}

