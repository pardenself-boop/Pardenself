"""Small, nonblocking updater using the existing TOOLBOXX visual palette."""
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from app_version import BUILD
from app_updates import check_for_update, download_update, verify_installer


class UpdateWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title('TOOLBOXX / UPDATES')
        self.win.geometry('580x340')
        self.win.configure(bg='#24201e')
        self.events = queue.Queue()
        self.update = None
        self.installer = None
        self.busy = False
        self.closed = False
        self.status = tk.StringVar(value='Check for a newer TOOLBOXX build when you are ready.')
        tk.Label(self.win, text='TOOLBOXX / KEEP IT FRESH', bg='#24201e', fg='#82ceb5', font=('Segoe UI', 17, 'bold')).pack(pady=(18, 8))
        tk.Label(self.win, text=f'Installed build: {BUILD} · Development update channel', bg='#24201e', fg='#e6d2b3').pack()
        tk.Label(self.win, textvariable=self.status, bg='#24201e', fg='#e6d2b3', wraplength=520, height=4).pack(padx=20, pady=10)
        self.progress = ttk.Progressbar(self.win, maximum=100)
        self.progress.pack(fill='x', padx=25)
        row = tk.Frame(self.win, bg='#24201e')
        row.pack(pady=18)
        self.check = tk.Button(row, text='CHECK FOR UPDATES', command=self.start_check, bg='#e38b42')
        self.check.pack(side='left', padx=5)
        self.download = tk.Button(row, text='DOWNLOAD', command=self.start_download, state='disabled')
        self.download.pack(side='left', padx=5)
        self.install = tk.Button(row, text='INSTALL UPDATE', command=self.install_update, state='disabled')
        self.install.pack(side='left', padx=5)
        tk.Label(self.win, text='Save your project before installing. Updates use the same installer.\nPublisher signing is not configured yet; Windows may show a warning.', bg='#24201e', fg='#ad9a84', wraplength=530).pack(padx=20)
        self.win.protocol('WM_DELETE_WINDOW', self.close)
        self.poll_id = self.win.after(100, self.poll)

    def worker(self, task, function):
        if self.busy:
            return
        self.busy = True
        for button in (self.check, self.download, self.install):
            button.config(state='disabled')
        def run():
            try:
                self.events.put((task, function()))
            except Exception as exc:
                self.events.put(('error', str(exc)))
        threading.Thread(target=run, daemon=True).start()

    def start_check(self):
        if self.busy:
            return
        self.update = None
        self.installer = None
        self.progress['value'] = 0
        self.status.set('Checking official TOOLBOXX releases…')
        self.worker('checked', lambda: check_for_update(BUILD))

    def start_download(self):
        if self.busy or self.update is None:
            return
        root = Path(os.environ.get('LOCALAPPDATA') or Path.home() / '.cache') / 'BOOM BAP TOOLBOXX' / 'Updates'
        self.status.set('Downloading the installer. You can keep using the DAW.')
        self.worker('downloaded', lambda: download_update(self.update, root, lambda done, total: self.events.put(('progress', done * 100 / total))))

    def poll(self):
        while not self.events.empty():
            task, value = self.events.get_nowait()
            if task == 'progress':
                self.progress['value'] = value
                continue
            self.busy = False
            self.check.config(state='normal')
            if task == 'checked':
                self.update = value
                if value is None:
                    self.status.set(f'You are up to date. Build {BUILD} is the newest available build.')
                else:
                    self.status.set(f'Build {value.build} is available. Download it, then save your project before installing.')
                    self.download.config(state='normal')
            elif task == 'downloaded':
                self.installer = value
                self.status.set('Download verified. Save your project, then click INSTALL UPDATE.')
                self.install.config(state='normal')
            else:
                self.status.set('Update could not finish: ' + value + '\nYour current installation is unchanged. Try checking again.')
        if not self.closed:
            self.poll_id = self.win.after(100, self.poll)

    def install_update(self):
        if not self.installer or self.busy:
            return
        if sys.platform != 'win32':
            messagebox.showinfo('Windows update', 'Installer updates run on Windows.', parent=self.win)
            return
        if not messagebox.askyesno('Install TOOLBOXX update', 'Have you saved your project?\n\nContinue to close TOOLBOXX and open the update installer?', parent=self.win):
            return
        try:
            verify_installer(self.installer, self.update)
            subprocess.Popen([str(self.installer)])
        except Exception as exc:
            messagebox.showerror('Update installer', str(exc), parent=self.win)
            return
        self.app.close()

    def close(self):
        self.closed = True
        self.win.after_cancel(self.poll_id)
        self.win.destroy()
