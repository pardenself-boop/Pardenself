param(
  [Parameter(Mandatory=$true)][string]$InputFile,
  [Parameter(Mandatory=$true)][ValidatePattern('^[a-fA-F0-9]{40}$')][string]$CertificateThumbprint,
  [string]$TimestampUrl = 'http://timestamp.digicert.com'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$path = (Resolve-Path -LiteralPath $InputFile).Path
$certificate = Get-Item -LiteralPath ('Cert:\CurrentUser\My\' + $CertificateThumbprint)
if (-not $certificate.HasPrivateKey) { throw 'The signing certificate has no accessible private key.' }
if ($certificate.NotAfter -le (Get-Date)) { throw 'The signing certificate has expired.' }
$signCommand = Get-Command signtool.exe -ErrorAction SilentlyContinue
if ($signCommand) { $signTool = $signCommand.Source }
else {
  $sdk = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\bin'
  $candidate = Get-ChildItem -Path $sdk -Filter signtool.exe -Recurse | Where-Object { $_.FullName -match '\\x64\\' } | Sort-Object FullName -Descending | Select-Object -First 1
  if (-not $candidate) { throw 'Install the Windows SDK signing tools on the signing machine.' }
  $signTool = $candidate.FullName
}
& $signTool sign /sha1 $CertificateThumbprint /fd SHA256 /tr $TimestampUrl /td SHA256 $path
if ($LASTEXITCODE -ne 0) { throw 'Code signing failed.' }
& $signTool verify /pa /all $path
if ($LASTEXITCODE -ne 0) { throw 'The signature did not pass Windows public-trust verification.' }
$signature = Get-AuthenticodeSignature -LiteralPath $path
if ($signature.Status -ne 'Valid') { throw ('Windows does not trust the signature: ' + $signature.StatusMessage) }
if (-not $signature.TimeStamperCertificate) { throw 'The signature has no verified timestamp.' }
Write-Host ('Verified publisher: ' + $signature.SignerCertificate.Subject)
