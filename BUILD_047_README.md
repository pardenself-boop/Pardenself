# BOOM BAP TOOLBOXX Build 047 — Audio startup recovery

- Engine now releases an output stream if opening or starting it fails, so a subsequent retry can work.
- Audio callback clears the output buffer before rendering, prevents non-finite samples from reaching output, and records DSP errors without propagating exceptions into the device callback.
- Main DAW output selector now offers **System default** first instead of selecting an arbitrary first audio device.
- Three new regression tests cover successful startup/stop, failed startup/retry, and callback silence on DSP errors.
- 53 automated tests passed on Linux. This is source code and Windows build scripts, not a compiled Setup.exe. Live Windows audio and Maschine Studio tests remain required.

To build the Windows installer, use BUILD_SETUP_DOUBLE_CLICK.cmd on Windows with internet access and the documented dependencies. For isolated audio testing, use TEST_AUDIO_DOUBLE_CLICK.cmd.
