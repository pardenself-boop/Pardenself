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
        for page in app.surface_context.PAGES:
            app.surface_context.set_page(page)
            app.controller_map_window.draw()
            root.update()
        app.surface_context.set_page('ARRANGE')
        before=app.labbs.serialize()
        app.open_sound_browser()
        root.update()
        assert app.labbs.serialize()==before, 'Opening the sound editor changed the patch'
        app.open_mix_rack()
        app.open_updates()
        assert app.update_window.win.winfo_exists(), 'Update window did not open'
        assert not app.update_window.busy, 'Updater started a background request without a click'
        app.open_audio_midi()
        assert app.audio_midi_window.win.winfo_exists(), 'Audio/MIDI setup did not open'
        assert app.engine.stream is None, 'Opening setup started audio automatically'
        assert app.midi_port is None, 'Opening setup connected MIDI automatically'
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
