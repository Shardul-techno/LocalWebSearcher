$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

& "$PSScriptRoot\fetch_llama_server.ps1"
& ".\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean packaging\lre.spec
& ".\dist\LocalResearch\lre.exe" selftest

$version = & ".\.venv\Scripts\python.exe" -c "from lre._version import __version__; print(__version__)"
$env:LRE_VERSION = $version
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if (-not $iscc) { throw "Inno Setup 6 (ISCC.exe) is required to build the installer." }
& $iscc.Source packaging\lre.iss

Compress-Archive -Path ".\dist\LocalResearch\*" -DestinationPath ".\dist\LocalResearch-$version-portable.zip" -Force
Get-FileHash ".\dist\LocalResearch-$version-portable.zip", ".\dist\LocalResearch-Setup-$version.exe" -Algorithm SHA256 |
    ForEach-Object { "{0}  {1}" -f $_.Hash.ToLowerInvariant(), $_.Path } |
    Set-Content ".\dist\SHA256SUMS.txt"
