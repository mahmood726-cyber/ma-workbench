param(
  [int]$Port = 8080,
  [switch]$Open
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command py -ErrorAction SilentlyContinue

if (-not $python) {
  $python = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $python) {
  throw "Python was not found. Install Python or run a local static server with another tool."
}

$url = "http://localhost:$Port/index.html"

Write-Host "Serving $root on http://localhost:$Port" -ForegroundColor Cyan
Write-Host "Hub URL: $url" -ForegroundColor Green

if ($Open) {
  Start-Process $url
}

if ($python.Name -eq "py.exe" -or $python.Name -eq "py") {
  & $python.Source -m http.server $Port --directory $root
} else {
  & $python.Source -m http.server $Port --directory $root
}
