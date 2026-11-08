import sys
from pathlib import Path
sys.path.insert(0,str(Path('app').resolve()))
import tkinter as tk
from types import SimpleNamespace
from toolboxx import App
root=tk.Tk();errors=[]
root.report_callback_exception=lambda kind,value,tb:errors.append(value)
app=App(root);app.open_cookup();root.withdraw();root.update()
app.open_hardware_setup();root.update();setup=app.hardware_setup_window
setup.command.set('BANK PAD 1');setup.command_changed();assert setup.mode.get()=='button'
setup.learn();assert app.hardware_learn
message=SimpleNamespace(type='note_on',channel=0,note=60,velocity=100)
app._enqueue_midi(message);app._poll();root.update()
assert app.hardware_learn is None
assert app.hardware_midi.bindings['note:0:60']['command']=='BANK PAD 1'
app.set_bank(1);app._enqueue_midi(message);app._poll();root.update()
assert app.selected_pad==16
# Learning a relative encoder preserves direction decoding.
setup.command.set('HW JOG');setup.command_changed();setup.learn()
encoder=SimpleNamespace(type='control_change',channel=0,control=1,value=1)
app._enqueue_midi(encoder);app._poll();root.update()
assert app.hardware_midi.translate(encoder)==['HW JOG +']
setup.poll();setup.win.geometry('980x650+100+100');setup.win.lift();root.update()
import subprocess
subprocess.run(['import','-display',':99','-window',str(setup.win.winfo_id()),'/workspace/work/maschine-setup060.png'],check=True)
setup.close();root.update();assert app.hardware_learn is None
assert not errors,errors
app.close()
print('PASS: actual Tk Maschine setup, note learn, bank-aware MIDI pad dispatch, encoder learn, close cancellation; no callback errors')
