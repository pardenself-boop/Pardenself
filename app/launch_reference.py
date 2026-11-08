"""Launch the existing COOK UP MATRIX layout shown in the approved reference screenshot.
No layout redesign; existing Tkinter DAW remains the authoritative implementation.
"""
import tkinter as tk
import sys
from toolboxx import App


def main():
    root = tk.Tk()
    app = App(root)
    def open_workspace():
        app.open_cookup()
        root.withdraw()
        app.cookup_window.win.protocol('WM_DELETE_WINDOW', app.close)
    root.after(150, open_workspace)
    if '--dual' in sys.argv:
        root.after(550, app.open_labbs)
    root.mainloop()


if __name__ == '__main__':
    main()
