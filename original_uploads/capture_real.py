import tkinter as tk
from toolboxx import App
root=tk.Tk();app=App(root)
root.after(350,app.open_cookup)
root.after(1350,lambda: __import__('os').system('scrot /mnt/data/BOOM_BAP_TOOLBOXX_v1.4_ACTUAL_UI.png'))
root.after(1700,root.destroy)
root.mainloop()
