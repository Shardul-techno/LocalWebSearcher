param([string]$Command = "doctor")
$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m lre $Command
