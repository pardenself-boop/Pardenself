"""Packaged TOOLBOXX entrypoint: main workstation or integrated sound check."""
import sys

def run(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
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
    run()
