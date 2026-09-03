# ---------------------------------------------------------------------------
# Setup script for Raster Images (Windows PowerShell).
#
# Creates a Python virtual environment in .\venv and installs this
# assignment's dependencies.
#
# Usage:
#     .\init.ps1                      # create venv and install dependencies
#     .\venv\Scripts\Activate.ps1      # then activate it in your shell
#
# If script execution is blocked, run:
#     powershell -ExecutionPolicy Bypass -File init.ps1
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

if (-not (Test-Path "venv")) {
    Write-Host "==> Creating virtual environment in .\venv"
    & $python -m venv venv
}

Write-Host "==> Installing dependencies"
& .\venv\Scripts\python.exe -m pip install --upgrade pip | Out-Null
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Done. Activate the environment in each new shell with:"
Write-Host ""
Write-Host "    .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Then:"
Write-Host ""
Write-Host "    python main.py           # run the demo backend"
Write-Host "    python run_tests.py      # check your implementation"
Write-Host "    python check_my_work.py  # see it scored as marks"
Write-Host ""
