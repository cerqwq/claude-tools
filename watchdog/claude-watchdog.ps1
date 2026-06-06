# Claude Code Watchdog
# Auto-restarts claude.exe if not running
# Stop: create DISABLE_WATCHDOG file or close window

$ErrorActionPreference = "SilentlyContinue"
$claudeCmd = "$env:APPDATA\npm\claude.cmd"
$checkInterval = 60
$disableFile = "$PSScriptRoot\DISABLE_WATCHDOG"
$logFile = "$PSScriptRoot\watchdog.log"

function Write-Log {
    param([string]$msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts  $msg" | Out-File -Append -FilePath $logFile -Encoding utf8
}

Write-Log "Watchdog started. PID=$PID"
Write-Log "Check interval: ${checkInterval}s"

while ($true) {
    if (Test-Path $disableFile) {
        Write-Log "DISABLE_WATCHDOG found. Exiting."
        Remove-Item $disableFile -Force
        break
    }

    $proc = Get-Process -Name "claude" -ErrorAction SilentlyContinue

    if (-not $proc) {
        Write-Log "Claude not running. Launching..."
        Start-Process -FilePath $claudeCmd -WindowStyle Hidden
        Start-Sleep -Seconds 5
        $proc = Get-Process -Name "claude" -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Log "Claude started. PID=$($proc.Id)"
        } else {
            Write-Log "WARNING: Failed to start Claude."
        }
    }

    Start-Sleep -Seconds $checkInterval
}
