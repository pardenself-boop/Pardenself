"""Packaged TOOLBOXX entrypoint: main workstation or integrated sound check."""
import sys

def run(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if '--smoke-test' in args:
        from startup_check import run as startup_check
        return startup_check()
    if '--sound-check' in args:
        import tkinter as tk
        from audio_smoke_test import AudioTest
        root = tk.Tk()
        AudioTest(root)
        root.mainloop()
        return 'sound-check'
    from launch_reference import main
    main()
    return 'workstation'

if __name__ == '__main__':
    result = run()
    if isinstance(result, int):
        sys.exit(result)
