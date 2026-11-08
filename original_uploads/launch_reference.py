"""Launch the existing COOK UP MATRIX layout shown in the approved reference screenshot.
No layout redesign; existing Tkinter DAW remains the authoritative implementation.
"""
import tkinter as tk
import sys
from toolboxx import App


def main():
    root = tk.Tk()
    app = App(root)
    root.after(150, app.open_cookup)
    if '--dual' in sys.argv:
        root.after(550, app.open_labbs)
    root.mainloop()


if __name__ == '__main__':
    main()
