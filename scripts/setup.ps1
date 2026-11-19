$ErrorActionPreference = "Stop"
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
& .\.venv\Scripts\python.exe -m pip freeze | Where-Object { $_ -notmatch "^-e " -and $_ -notmatch "^lre==" } | Set-Content requirements.lock.txt
& .\.venv\Scripts\python.exe -m pytest
