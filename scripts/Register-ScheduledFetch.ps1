[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$TaskName = "RM Trend Radar RSS Fetch",
    [string]$At = "14:37",
    [double]$TimeoutSeconds = 20,
    [string]$PythonPath,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$FetchScript = Join-Path $PSScriptRoot "Invoke-ScheduledFetch.ps1"

if (-not (Test-Path -LiteralPath $FetchScript)) {
    Write-Error "Fetch script was not found: $FetchScript"
    exit 1
}

$ArgumentParts = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    ('"{0}"' -f $FetchScript),
    "-TimeoutSeconds",
    ([string]$TimeoutSeconds)
)

if ($PythonPath) {
    $ArgumentParts += @("-PythonPath", ('"{0}"' -f $PythonPath))
}

if ($DryRun) {
    $ArgumentParts += "-DryRun"
}

$TaskRun = "powershell.exe " + ($ArgumentParts -join " ")

if ($PSCmdlet.ShouldProcess($TaskName, "Register scheduled fetch task")) {
    & schtasks.exe /Create /TN $TaskName /TR $TaskRun /SC DAILY /ST $At /F
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Write-Output "Scheduled task: $TaskName"
Write-Output "Daily time: $At"
Write-Output "Action: $TaskRun"
