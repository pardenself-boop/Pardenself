param([switch]$NoOpen)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location $PSScriptRoot
$release = Get-Content (Join-Path $PSScriptRoot 'release.json') -Raw | ConvertFrom-Json
$log = Join-Path $PSScriptRoot ('BUILD_' + $release.build + '_LOG.txt')
Start-Transcript -Path $log -Force | Out-Null
try {
  Write-Host ("BOOM BAP TOOLBOXX - Build " + $release.build + " Windows installer") -ForegroundColor Cyan
  if ($env:OS -ne 'Windows_NT') { throw 'This builder requires Windows.' }
  if (-not [Environment]::Is64BitOperatingSystem) { throw 'Windows 11 64-bit is required.' }
  $py = Get-Command py -ErrorAction SilentlyContinue
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py -and -not $python) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Python 3.11 missing. Install Python 3.11 or Windows App Installer (winget), then retry.' }
    winget install --id Python.Python.3.11 --exact --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) { throw 'Python installation failed.' }
    $py = Get-Command py -ErrorAction SilentlyContinue
    $python = Get-Command python -ErrorAction SilentlyContinue
  }
  if ($py) { $pythonExe = 'py'; $pythonArgs = @('-3.11') }
  elseif ($python) { $pythonExe = $python.Source; $pythonArgs = @() }
  else { throw 'Python installed but not yet available. Reopen the builder and retry.' }
  & $pythonExe @pythonArgs -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
  if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or newer is required.' }
  & $pythonExe @pythonArgs -m venv '.builder-venv'
  if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated builder environment.' }
  $venvPy = Join-Path $PSScriptRoot '.builder-venv\Scripts\python.exe'
  & $venvPy -m pip install --disable-pip-version-check -r '.\requirements-build.txt'
  if ($LASTEXITCODE -ne 0) { throw 'Python dependencies failed to install; see build log.' }
  & $venvPy -m unittest discover -s tests -v
  if ($LASTEXITCODE -ne 0) { throw 'Regression tests failed.' }
  & $venvPy -m pip freeze | Out-File -Encoding utf8 (Join-Path $PSScriptRoot 'BUILD_DEPENDENCIES.txt')
  & $venvPy -m compileall -q '.\app'
  if ($LASTEXITCODE -ne 0) { throw 'Source syntax check failed.' }
  & $venvPy '.\verify_package.py'
  if ($LASTEXITCODE -ne 0) { throw 'Package preflight failed.' }
  & $venvPy -m PyInstaller --noconfirm --clean --windowed --onedir --name BOOM_BAP_TOOLBOXX --distpath '.\build' --workpath '.\work' --specpath '.\work' --paths (Join-Path $PSScriptRoot 'app') --add-data ((Join-Path $PSScriptRoot 'app\AUDIO_TEST.wav') + ';.') --collect-all sounddevice --collect-all soundcard --collect-all numpy --collect-all mido --collect-all rtmidi --collect-all PIL '.\app\toolboxx_launcher.py'
  if ($LASTEXITCODE -ne 0) { throw 'Executable packaging failed.' }
  $exe = Join-Path $PSScriptRoot 'build\BOOM_BAP_TOOLBOXX\BOOM_BAP_TOOLBOXX.exe'
  if (-not (Test-Path $exe)) { throw 'Packaged application executable missing.' }
  $smoke = Start-Process -FilePath $exe -ArgumentList '--smoke-test' -PassThru
  if (-not $smoke.WaitForExit(60000)) { $smoke.Kill(); throw 'Packaged startup timed out.' }
  if ($smoke.ExitCode -ne 0) { throw 'Packaged startup failed.' }
  $isccPaths = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe")
  $iscc = $isccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
  if (-not $iscc) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Inno Setup 6 missing; install it and rerun the builder.' }
    winget install --id JRSoftware.InnoSetup --exact --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup installation failed.' }
    $iscc = $isccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
  }
  if (-not $iscc) { throw 'Inno Setup installed but not found; reopen builder and retry.' }
  $installerBase = [IO.Path]::GetFileNameWithoutExtension($release.installer)
  & $iscc ('/DMyAppVersion=' + $release.version) ('/DInstallerBase=' + $installerBase) '.\installer\toolboxx.iss'
  if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed.' }
  $setup = Join-Path $PSScriptRoot ('dist\' + $release.installer)
  if (-not (Test-Path $setup)) { throw 'Setup.exe output missing.' }
  & $venvPy '.\verify_release.py'
  if ($LASTEXITCODE -ne 0) { throw 'Release artifact validation failed.' }
  Get-FileHash -Algorithm SHA256 $setup | Format-List | Out-File -Encoding utf8 '.\dist\SHA256.txt'
  Write-Host "SUCCESS: $setup" -ForegroundColor Green
  Write-Host 'This installer is unsigned and needs Windows 11 installation and hardware testing.'
  if (-not $NoOpen) { Invoke-Item (Join-Path $PSScriptRoot 'dist') }
} catch {
  Write-Host "BUILD FAILED: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host "Build log: $log" -ForegroundColor Yellow
  exit 1
} finally {
  Stop-Transcript | Out-Null
}
