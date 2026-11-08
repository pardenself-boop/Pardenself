import tkinter as tk
from toolboxx import App
root=tk.Tk();app=App(root)
def show():
 app.open_cookup();root.withdraw()
root.after(250,show)
root.after(1800,lambda:__import__('subprocess').run(['scrot','/mnt/data/BOOM_BAP_TOOLBOXX_v1.5_ACTUAL_UI.png']))
root.after(2300,root.destroy)
root.mainloop()
