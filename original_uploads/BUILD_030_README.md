# BOOM BAP TOOLBOXX Build 030 — Release integrity pass

This is a **Windows installer builder**, not a precompiled Windows installer.

## What changed
- Versioned installer output to `BOOM_BAP_TOOLBOXX_Setup_030.exe`.
- Added `verify_release.py`: checks that the packaged application executable and final setup executable exist, are nonempty and have a minimum size, and prints a SHA-256 checksum.
- Integrated artifact validation into the Windows builder before reporting success.
- Renamed build transcript and checksum output for Build 030.
- Kept existing DAW application code and approved UI untouched.

## Windows 11 build
1. Extract the ZIP to a normal writable folder.
2. Double-click `BUILD_SETUP_DOUBLE_CLICK.cmd` on your own trusted PC.
3. Wait for the script to finish. If successful, the setup file is in `dist/`.
4. Install it on a test Windows 11 system. Confirm that the application opens, that audio output works, and that your Maschine Studio and Logitech Trackman Marble work.

**Do not distribute the setup file until the installation and hardware tests pass.** It is unsigned, so Windows SmartScreen may warn. No Windows executable was compiled in this environment.
