$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$ProfilePath = Join-Path $env:USERPROFILE ".neurogate-usage-overlay\browser-profile"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment not found. Installing first..."
    & (Join-Path $Root "scripts\install.ps1")
}

# Keep one overlay instance. Multiple instances fight for the same Chrome
# profile and can show empty values. Match old global installs too: early
# public builds could be started with a global Python instead of this .venv.
Get-CimInstance Win32_Process |
    Where-Object {
        (
            ($_.Name -in @('python.exe', 'pythonw.exe', 'py.exe') -and $_.CommandLine -match 'neurogate_usage_overlay|neurogate-overlay|neurogate-api|vibemode-overlay|neurogate-usage-overlay') -or
            ($_.Name -eq 'node.exe' -and $_.CommandLine -match [regex]::Escape($Root)) -or
            ($_.Name -eq 'chrome.exe' -and $_.CommandLine -match [regex]::Escape($ProfilePath))
        )
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

& $VenvPython -m neurogate_usage_overlay --interval 60
