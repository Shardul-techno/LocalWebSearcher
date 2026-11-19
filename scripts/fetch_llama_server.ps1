$ErrorActionPreference = "Stop"
$lock = Get-Content -Raw third_party\llama_server.lock.toml
$match = [regex]::Match($lock, 'sha256\s*=\s*"([0-9A-Fa-f]*)"')
if (-not $match.Success -or [string]::IsNullOrWhiteSpace($match.Groups[1].Value)) {
    Write-Host "Refusing to download llama-server: third_party/llama_server.lock.toml has no verified SHA-256."
    exit 1
}

$url = [regex]::Match($lock, 'url\s*=\s*"([^"]+)"').Groups[1].Value
$expected = $match.Groups[1].Value.ToUpperInvariant()
$temporary = New-TemporaryFile
$zip = "$($temporary.FullName).zip"
Remove-Item -LiteralPath $temporary.FullName
Invoke-WebRequest -Uri $url -OutFile $zip
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash -ne $expected) {
    Remove-Item -LiteralPath $zip
    throw "llama-server SHA-256 did not match the lock file."
}
New-Item -ItemType Directory -Force bin | Out-Null
Expand-Archive -LiteralPath $zip -DestinationPath bin -Force
Remove-Item -LiteralPath $zip
if (-not (Test-Path bin\llama-server.exe)) { throw "Release archive did not contain bin\\llama-server.exe" }
