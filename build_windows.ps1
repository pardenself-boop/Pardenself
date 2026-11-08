param([switch]$NoOpen)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'BUILD_SETUP_WINDOWS.ps1') -NoOpen:$NoOpen
