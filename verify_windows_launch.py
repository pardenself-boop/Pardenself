"""Check the customer's normal installed launch, without a special app mode."""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import time


def verify(executable, screenshot=None):
    if os.name != 'nt':
        raise RuntimeError('This check requires a Windows desktop session')
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    process = subprocess.Popen([str(Path(executable).resolve())])

    def visible_windows():
        found = []
        @callback_type
        def visit(hwnd, _):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == process.pid and user32.IsWindowVisible(hwnd):
                text = ctypes.create_unicode_buffer(user32.GetWindowTextLengthW(hwnd) + 1)
                user32.GetWindowTextW(hwnd, text, len(text))
                found.append((hwnd, text.value))
            return True
        user32.EnumWindows(visit, 0)
        return found

    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Normal launch exited early: {process.returncode}')
            windows = visible_windows()
            workspace = [(hwnd, title) for hwnd, title in windows if 'COOK UP MATRIX' in title]
            if workspace:
                break
            time.sleep(.2)
        else:
            raise RuntimeError('Normal launch did not show Cook Up within 30 seconds')
        time.sleep(1)
        windows = visible_windows()
        assert len(workspace) == 1, f'Expected one Cook Up window: {windows}'
        assert not any('COOK UP v1.4' in title for _, title in windows), 'Underlying workstation was not hidden'
        hwnd, title = workspace[0]
        release = json.loads(Path(__file__).with_name('release.json').read_text())
        assert 'BUILD ' + release['build'] in title, f'Wrong installed build: {title}'
        if screenshot:
            from PIL import ImageGrab
            rect = wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                raise ctypes.WinError(ctypes.get_last_error())
            assert rect.right > rect.left and rect.bottom > rect.top, 'Workspace has no visible size'
            destination = Path(screenshot)
            destination.parent.mkdir(parents=True, exist_ok=True)
            ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom)).save(destination)
        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE through the app's normal handler.
        if process.wait(timeout=15) != 0:
            raise RuntimeError(f'Normal app close failed: {process.returncode}')
        print('PASS: normal installed launch, one visible Cook Up workspace, correct build, clean close')
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', required=True)
    parser.add_argument('--screenshot')
    args = parser.parse_args()
    verify(args.exe, args.screenshot)
