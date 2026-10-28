# Owner-approved, one-time recovery only. Never called by model tools or normal startup.
param([switch]$ApproveServiceRestart, [switch]$FinishPendingRestart)
$ErrorActionPreference = 'Stop'
$resultPath = Join-Path $env:LOCALAPPDATA 'CodexDesktopAssistant\service-recovery.json'
try {
if (-not $ApproveServiceRestart) { throw 'Explicit owner approval is required.' }
if ($FinishPendingRestart) {
    $service = Get-CimInstance Win32_Service -Filter "Name='WslService'"
    if ($service.State -ne 'Stop Pending') { throw 'The WSL service is not stuck stopping; refusing forced recovery.' }
    if (Get-Process -Name vmmemWSL -ErrorAction SilentlyContinue) { throw 'A WSL VM is present; refusing forced recovery.' }
    $serviceProcessId = [int]$service.ProcessId
    if ($serviceProcessId -le 0) { throw 'No verified service process.' }
    $shared = @(Get-CimInstance Win32_Service -Filter "ProcessId=$serviceProcessId")
    $process = Get-Process -Id $serviceProcessId
    if ($shared.Count -ne 1 -or $process.ProcessName -ne 'wslservice') { throw 'Service process identity is not exclusive WSL.' }
    Stop-Process -Id $serviceProcessId -Force
    Start-Sleep -Seconds 2
    if ((Get-Service WslService).Status -ne 'Running') { Start-Service WslService }
} else {
$runningBytes = & wsl.exe --list --running --quiet 2>&1
if ($LASTEXITCODE -ne 0) { throw 'Could not verify that distributions are stopped.' }
$runningText = (($runningBytes | Out-String) -replace "`0", '').Trim()
if ($runningText) { throw 'A WSL distribution is running. No service was restarted.' }
Restart-Service -Name WslService -ErrorAction Stop
}
Write-Output 'WSL service restarted; no running distributions were stopped.'
[System.IO.File]::WriteAllText($resultPath, '{"service_restarted":true,"running_distributions_stopped":false}')
} catch {
    [System.IO.File]::WriteAllText($resultPath, (@{service_restarted=$false;error=$_.Exception.Message} | ConvertTo-Json))
    throw
}
