import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from ui_shortcuts import dispatch_shortcut
from toolboxx import App


class ShortcutSafetyTests(unittest.TestCase):
    def test_editing_text_does_not_change_arrangement(self):
        for widget_class in ('Entry', 'TEntry', 'Text', 'Spinbox', 'TSpinbox', 'TCombobox'):
            with self.subTest(widget_class=widget_class):
                action = Mock()
                widget = Mock()
                widget.winfo_class.return_value = widget_class
                self.assertIsNone(dispatch_shortcut(SimpleNamespace(widget=widget), action))
                action.assert_not_called()

    def test_canvas_command_runs_once_and_stops_propagation(self):
        action = Mock()
        widget = Mock()
        widget.winfo_class.return_value = 'Canvas'
        self.assertEqual(dispatch_shortcut(SimpleNamespace(widget=widget), action), 'break')
        action.assert_called_once_with()


class ShutdownSafetyTests(unittest.TestCase):
    def make_app(self):
        app = App.__new__(App)
        app.root = Mock()
        app.engine = Mock()
        app.close_midi = Mock()
        app.tick_id = 'scheduled-transport'
        app.playing = True
        return app

    def test_shutdown_cancels_transport_and_releases_devices_once(self):
        app = self.make_app()
        app.close()
        app.close()
        self.assertFalse(app.playing)
        app.root.after_cancel.assert_called_once_with('scheduled-transport')
        app.close_midi.assert_called_once_with()
        app.engine.stop.assert_called_once_with()
        app.root.destroy.assert_called_once_with()

    def test_midi_failure_still_releases_audio_and_window(self):
        app = self.make_app()
        app.close_midi.side_effect = RuntimeError('device unplugged')
        app.close()
        app.engine.stop.assert_called_once_with()
        app.root.destroy.assert_called_once_with()

    def test_audio_failure_still_destroys_window(self):
        app = self.make_app()
        app.engine.stop.side_effect = RuntimeError('device unplugged')
        with self.assertRaises(RuntimeError):
            app.close()
        app.root.destroy.assert_called_once_with()
