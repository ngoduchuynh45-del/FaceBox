$exe = 'C:\FaceBoxApp\FaceBox.exe'
$workDir = 'C:\FaceBoxApp'

Write-Host '=== Khoi dong FaceBox.exe ==='
Write-Host "EXE: $exe"
Write-Host "Exists: $(Test-Path $exe)"

$proc = Start-Process -FilePath $exe -WorkingDirectory $workDir -PassThru
Write-Host "PID: $($proc.Id)"

# Cho app khoi dong 10 giay
Start-Sleep -Seconds 10

$proc.Refresh()
if (-not $proc.HasExited) {
    Write-Host "STATUS: RUNNING OK"
    Write-Host "MainWindowTitle: $($proc.MainWindowTitle)"
    Write-Host "Responding: $($proc.Responding)"
    Write-Host "WorkingSet64: $([math]::Round($proc.WorkingSet64/1MB, 1)) MB"
    
    # Doi them 3 giay roi dong
    Start-Sleep -Seconds 3
    $proc.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 3
    
    if (-not $proc.HasExited) {
        $proc.Kill()
        Write-Host "Process killed forcefully"
    } else {
        Write-Host "Process closed gracefully"
    }
    Write-Host "ExitCode: $($proc.ExitCode)"
} else {
    Write-Host "STATUS: EXITED IMMEDIATELY (CRASH)"
    Write-Host "ExitCode: $($proc.ExitCode)"
}

# Kiem tra log
$logDir = Join-Path $workDir 'logs'
if (Test-Path $logDir) {
    $latest = Get-ChildItem $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) {
        Write-Host ""
        Write-Host "=== Latest log: $($latest.Name) ==="
        Get-Content $latest.FullName -Tail 30
    }
} else {
    Write-Host "No logs directory found"
}

