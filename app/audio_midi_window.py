"""Audio/MIDI setup for the existing shared workstation engine and MIDI port."""
import time
import tkinter as tk
from tkinter import ttk
from app_version import BUILD

BG = '#24201e'
CREAM = '#e6d2b3'
MINT = '#82ceb5'
ORANGE = '#e38b42'


class AudioMidiWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title('TOOLBOXX / AUDIO + MIDI SETUP')
        self.win.geometry('780x680')
        self.win.minsize(700, 620)
        self.win.configure(bg=BG)
        self.status = tk.StringVar(value='Choose an output and start audio. Connect Studio MIDI separately.')
        self.output = tk.StringVar(value=app.audio_device.get())
        self.input = tk.StringVar(value=app.midi_device.get())
        self.audio_status = tk.StringVar()
        self.midi_status = tk.StringVar()
        self.last_count = -1
        self.label('TOOLBOXX / AUDIO + MIDI', 17, MINT).pack(pady=(15, 8))
        self.label('Shared with Cook Up · one audio engine · one MIDI connection', 10).pack()
        self.label('1 / AUDIO OUTPUT', 12, ORANGE).pack(anchor='w', padx=22, pady=(15, 5))
        row = self.row()
        self.outputs = ttk.Combobox(row, textvariable=self.output, values=[name for name, _ in app.audio_choices], state='readonly', width=57)
        self.outputs.pack(side='left', fill='x', expand=True)
        self.button(row, 'SCAN', self.scan_audio).pack(side='left', padx=(8, 0))
        row = self.row()
        for label, action in [('START AUDIO', self.start_audio), ('STOP AUDIO', self.stop_audio), ('TEST BASS', lambda: self.test_note(3, 36)), ('TEST KEYS', lambda: self.test_note(7, 60))]:
            self.button(row, label, action).pack(side='left', padx=(0, 8))
        self.label_variable(self.audio_status).pack(anchor='w', padx=23)
        self.meter = ttk.Progressbar(self.win, maximum=100)
        self.meter.pack(fill='x', padx=23, pady=7)
        self.label('2 / MASCHINE STUDIO MIDI INPUT', 12, ORANGE).pack(anchor='w', padx=22, pady=(10, 5))
        row = self.row()
        self.inputs = ttk.Combobox(row, textvariable=self.input, values=list(app.midi_device['values']), state='readonly', width=57)
        self.inputs.pack(side='left', fill='x', expand=True)
        self.button(row, 'SCAN', self.scan_midi).pack(side='left', padx=(8, 0))
        row = self.row()
        for label, action in [('CONNECT', self.connect), ('DISCONNECT', self.disconnect), ('LEARN / STUDIO MAP', app.open_dual_screen)]:
            self.button(row, label, action).pack(side='left', padx=(0, 8))
        self.label('Studio MIDI mode: SHIFT + CHANNEL. Close other apps using the same MIDI port.', 9).pack(anchor='w', padx=23)
        row = self.row()
        self.led = self.label('● MIDI IN', 11, '#713a33', parent=row)
        self.led.pack(side='left', padx=(0, 15))
        self.label_variable(self.midi_status, parent=row).pack(side='left')
        self.log = tk.Text(self.win, height=7, bg='#161516', fg=MINT, font=('Consolas', 10), state='disabled', wrap='none')
        self.log.pack(fill='both', expand=True, padx=23, pady=7)
        self.label_variable(self.status).pack(fill='x', padx=23, pady=7)
        row = self.row()
        self.button(row, 'COPY TEST REPORT', self.copy_report).pack(side='left')
        self.label('Closing this window keeps your audio and MIDI connected.', 9, parent=row).pack(side='left', padx=12)
        self.win.protocol('WM_DELETE_WINDOW', self.close)
        self.poll()

    def row(self):
        row = tk.Frame(self.win, bg=BG)
        row.pack(fill='x', padx=23, pady=5)
        return row

    def label(self, text, size=10, color=CREAM, parent=None):
        return tk.Label(parent or self.win, text=text, bg=BG, fg=color, font=('Segoe UI', size))

    def label_variable(self, variable, parent=None):
        return tk.Label(parent or self.win, textvariable=variable, bg=BG, fg=CREAM, wraplength=700, justify='left')

    def button(self, parent, text, action):
        return tk.Button(parent, text=text, command=action, bg='#38243d', fg=CREAM, activebackground=ORANGE, activeforeground=BG, font=('Segoe UI', 9, 'bold'), padx=8, pady=5)

    def scan_audio(self):
        selected = self.output.get()
        self.app.scan_audio()
        names = [name for name, _ in self.app.audio_choices]
        self.outputs['values'] = names
        self.output.set(selected if selected in names else self.app.audio_device.get())
        self.status.set('Audio outputs refreshed.' if names else 'No outputs found. Check your interface driver and try SCAN again.')

    def start_audio(self):
        if self.output.get() not in [name for name, _ in self.app.audio_choices]:
            self.status.set('Select an audio output first. Use SCAN if the list is empty.')
            return
        self.app.audio_device.set(self.output.get())
        if self.app.start_audio():
            self.status.set('Audio started. Click TEST BASS or TEST KEYS, then listen to your selected output.')
        else:
            self.status.set(self.app.engine.audio_status)

    def stop_audio(self):
        try:
            self.app.engine.stop()
            self.status.set('Audio stopped.')
        except Exception as exc:
            self.status.set('Could not stop audio: ' + str(exc))

    def test_note(self, instrument, note):
        if self.app.engine.stream is None:
            self.status.set('Click START AUDIO before testing a note.')
            return
        self.app.labbs.note_on(note=note, velocity=.65, labb=instrument, duration=.65)
        self.status.set('Test note sent through your current instruments and master FX. No project edits made.')

    def scan_midi(self):
        selected = self.input.get()
        names = self.app.scan_midi()
        self.inputs['values'] = names
        self.input.set(selected if selected in names else self.app.midi_device.get())
        self.status.set('Choose the Studio input, then CONNECT.' if names else self.app.hardware_status)

    def connect(self):
        self.app.midi_device.set(self.input.get())
        self.app.open_midi()
        self.status.set(self.app.hardware_status)

    def disconnect(self):
        try:
            self.app.close_midi()
            self.status.set(self.app.hardware_status)
        except Exception as exc:
            self.status.set('MIDI disconnect: ' + str(exc))

    def poll(self):
        engine = self.app.engine
        self.audio_status.set(engine.audio_status)
        self.meter['value'] = self.app.labbs.master.peak * 100 if engine.stream is not None else 0
        activity = self.app.midi_activity
        active = activity.last_received is not None and time.monotonic() - activity.last_received < .35
        self.led.config(fg=MINT if active else '#713a33')
        connection = self.app.midi_connected_name or 'Not connected'
        self.midi_status.set(f'{connection} · {activity.count} messages')
        if activity.count != self.last_count:
            self.last_count = activity.count
            self.log.config(state='normal')
            self.log.delete('1.0', 'end')
            self.log.insert('end', '\n'.join(activity.entries))
            self.log.see('end')
            self.log.config(state='disabled')
        self.poll_id = self.win.after(100, self.poll)

    def copy_report(self):
        report = f'TOOLBOXX Build {BUILD}\nAudio: {self.app.engine.audio_status}\nSelected output: {self.output.get()}\nMIDI: {self.app.midi_connected_name or "Not connected"}\nStatus: {self.app.hardware_status}\nRecent MIDI:\n' + '\n'.join(self.app.midi_activity.entries)
        self.win.clipboard_clear()
        self.win.clipboard_append(report)
        self.status.set('Test report copied. You can paste it into chat.')

    def close(self):
        self.win.after_cancel(self.poll_id)
        self.win.destroy()
