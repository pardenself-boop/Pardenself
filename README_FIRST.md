# BOOM BAP TOOLBOXX — Windows Installer Build Kit 024

**This archive is the installer build kit, NOT a ready-to-run Windows installer.**

The intended end-user deliverable is a single `BOOM_BAP_TOOLBOXX_Setup_024.exe`, created on Windows with the supplied build workflow. The installer will copy bundled application files to the current user's local app directory, create Start Menu shortcuts, optionally create a desktop shortcut, and offer to launch the DAW after installation. Uninstall is handled through Windows Installed Apps.

## Simplest build path

1. Put this entire folder into a GitHub repository.
2. In GitHub Actions run **Windows installer** via **Run workflow**.
3. Download the resulting artifact and extract its one `BOOM_BAP_TOOLBOXX_Setup_024.exe` file.
4. On your Windows PC, double-click that Setup.exe to install.

Alternative: on Windows, install Python 3.11 and Inno Setup 6, then run `powershell -ExecutionPolicy Bypass -File .\build_windows.ps1` from this directory.

## Important limitations

- No compiled Windows `.exe` is included here. Windows compilation and an actual install/uninstall test have **not** been run in this Linux environment.
- The build is **unsigned** and may display Windows SmartScreen warnings. Do not bypass security warnings without verifying the build's origin; production distribution needs code signing and malware scanning.
- No MIDI drivers or audio drivers are installed. Hardware must already be recognized by Windows.
- This packages the existing Build 023 DAW; it does not imply that all instrument DSP, presets, VST3 export, or physical hardware support are finished.
- Never delete earlier working versions or project backups during testing.
