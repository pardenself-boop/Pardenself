$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'BUILD_SETUP_WINDOWS.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
