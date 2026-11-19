param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments = @("doctor"))
$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m lre @Arguments
