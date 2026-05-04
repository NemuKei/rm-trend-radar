param(
    [string]$PythonPath,
    [double]$TimeoutSeconds = 20,
    [string[]]$Source = @(),
    [switch]$DryRun,
    [string]$LogDirectory
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $PythonPath) {
    $PythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
}
if (-not $LogDirectory) {
    $LogDirectory = Join-Path $RepoRoot "logs"
}

if (-not (Test-Path -LiteralPath $PythonPath)) {
    Write-Error "Python executable was not found: $PythonPath"
    exit 1
}

New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null

$FetchArgs = @(
    "-m",
    "rm_trend_radar",
    "fetch",
    "--json",
    "--timeout",
    ([string]$TimeoutSeconds)
)

foreach ($SourceName in $Source) {
    if ($SourceName) {
        $FetchArgs += @("--source", $SourceName)
    }
}

if ($DryRun) {
    $FetchArgs += "--dry-run"
}

function ConvertTo-CommandLineArgument {
    param([string]$Value)

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    return '"' + ($Value -replace '"', '\"') + '"'
}

$StartedAt = Get-Date
$LogPath = Join-Path $LogDirectory ("scheduled-fetch-{0}.jsonl" -f $StartedAt.ToString("yyyyMMdd"))
$PreviousPythonUtf8 = $env:PYTHONUTF8
$env:PYTHONUTF8 = "1"

try {
    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $PythonPath
    $StartInfo.WorkingDirectory = $RepoRoot
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.Arguments = ($FetchArgs | ForEach-Object { ConvertTo-CommandLineArgument $_ }) -join " "

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo
    [void]$Process.Start()
    $StdoutText = $Process.StandardOutput.ReadToEnd()
    $StderrText = $Process.StandardError.ReadToEnd()
    $Process.WaitForExit()
    $ExitCode = $Process.ExitCode
}
finally {
    if ($null -eq $PreviousPythonUtf8) {
        Remove-Item Env:\PYTHONUTF8 -ErrorAction SilentlyContinue
    }
    else {
        $env:PYTHONUTF8 = $PreviousPythonUtf8
    }
}

$Stdout = @($StdoutText -split "\r?\n" | Where-Object { $_ -ne "" })
$Stderr = @($StderrText -split "\r?\n" | Where-Object { $_ -ne "" })

$FinishedAt = Get-Date
$LogEntry = [ordered]@{
    started_at = $StartedAt.ToString("o")
    finished_at = $FinishedAt.ToString("o")
    exit_code = $ExitCode
    repo_root = $RepoRoot
    python_path = $PythonPath
    args = $FetchArgs
    stdout = @($Stdout | ForEach-Object { [string]$_ })
    stderr = @($Stderr | ForEach-Object { [string]$_ })
}

($LogEntry | ConvertTo-Json -Depth 5 -Compress) | Add-Content -Path $LogPath -Encoding UTF8

$Stdout | ForEach-Object { Write-Output $_ }
$Stderr | ForEach-Object { Write-Output $_ }
exit $ExitCode
