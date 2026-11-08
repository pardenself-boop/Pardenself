# BOOM BAP TOOLBOXX — Build 027 Installer Builder

This is a **builder ZIP**, not a compiled Setup.exe. No installer has been run on Windows yet.

## GitHub Actions (Windows 11 friendly)
1. Sign into GitHub and create a **private** repository (e.g. `boom-bap-toolboxx-installer`).
2. Upload the **contents** of this ZIP, keeping `.github/workflows/windows-installer.yml` at the repository root. GitHub's browser upload can omit hidden `.github` directories; if the workflow is missing, use GitHub Desktop to commit/push the unzipped folder instead.
3. Open repository **Actions** → **Build TOOLBOXX Windows Installer** → **Run workflow**.
4. After a successful run, open the run and download the `BOOM_BAP_TOOLBOXX_Setup_027` artifact. Unzip it to find **one Setup.exe**.
5. On Windows 11, inspect the downloaded file and double-click the Setup.exe. Follow prompts and select desktop shortcut.

GitHub workflow permissions must allow Actions; an account/repository is required. If compilation fails, share the failing log. Do not upload private samples, passwords or paid plugins.

## Limits
- Windows installer **not yet compiled or installation-tested**.
- No code signing; Windows may warn about an unknown publisher.
- This is a packaged Build 026 prototype, **not** a finished DAW/VST or verified Maschine Studio integration.
- Installer targets current-user installation; does not modify existing DAW projects or install audio/MIDI drivers.
