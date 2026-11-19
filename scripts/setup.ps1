$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python Launcher was not found. Install Python 3.11 from https://www.python.org/downloads/windows/"
    exit 1
}

& py -3.11 -c "import sys; assert sys.version_info[:2] == (3, 11)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.11 was not found. Install it from https://www.python.org/downloads/windows/"
    exit 1
}

& py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt -r requirements-dev.lock.txt
& .\.venv\Scripts\python.exe -m pip install -e .
& .\.venv\Scripts\python.exe -m pytest -q
