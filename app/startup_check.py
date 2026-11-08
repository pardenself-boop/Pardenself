"""Exercise real Tk windows without starting playback or connecting MIDI."""
import tkinter as tk
from toolboxx import App


def run():
    root = tk.Tk()
    errors = []
    root.report_callback_exception = lambda kind, value, tb: errors.append(value)
    app = None
    try:
        app = App(root)
        app.open_cookup()
        root.update()
        window = app.cookup_window
        assert window.win.winfo_exists(), 'Cook Up window did not open'
        assert window.labb_list.size() == 22, 'Missing LABB navigation'
        assert len(app.pattern) == 32, 'Missing sample pads'
        app.open_dual_screen()
        assert app.controller_map_window.canvas.winfo_exists(), 'Controller surface did not open'
        before=app.labbs.serialize()
        app.open_sound_browser()
        root.update()
        assert app.labbs.serialize()==before, 'Opening the sound editor changed the patch'
        app.open_mix_rack()
        window.refresh()
        root.update()
        if errors:
            raise RuntimeError(f'Tk callback failed: {errors[0]}') from errors[0]
        print('PASS: workstation, Cook Up and controller map, sound browser and FX startup; 22 LABBs, 32 pads')
        return 0
    finally:
        if app is not None:
            app.close()
        else:
            root.destroy()
