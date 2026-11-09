import queue
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from audio_midi_window import AudioMidiWindow
from midi_activity import MidiActivity
from toolboxx import App, Engine
from midi_automation_engine import MidiAutomationEngine
from studio_midi_adapter import MidiControlRouter
from street_midi_dispatch import StreetMidiDispatch


class Choice:
    def __init__(self, selected=''):
        self.selected = selected
        self.values = []
    def get(self):return self.selected
    def set(self, selected):self.selected = selected
    def __setitem__(self, key, value):self.values = value
    def current(self, index=None):
        if index is not None:self.selected = self.values[index]
        return self.values.index(self.selected) if self.selected in self.values else -1


class ActivityTests(unittest.TestCase):
    def test_bounded_note_cc_log_and_one_based_channel(self):
        activity = MidiActivity(limit=2)
        for kind, number, value in [('note_on', 36, 100), ('note_off', 36, 0), ('control_change', 10, 127)]:
            event = SimpleNamespace(type=kind, channel=2, note=number, control=number, velocity=value, value=value)
            self.assertTrue(activity.record(event))
        self.assertEqual(activity.count, 3)
        self.assertEqual(len(activity.entries), 2)
        self.assertIn('CH 03', activity.entries[-1])
        self.assertIn('CC 010', activity.entries[-1])
        self.assertIsNotNone(activity.last_received)

    def test_invalid_and_realtime_messages_do_not_fill_monitor(self):
        activity = MidiActivity()
        for event in (SimpleNamespace(type='clock'), SimpleNamespace(type='note_on', channel=0, note=128, velocity=50), SimpleNamespace(type='note_on', channel=0, note=36, velocity=True)):
            self.assertFalse(activity.record(event))
        self.assertEqual(activity.count, 0)

    def test_monitor_observes_learn_message_without_dispatching_twice(self):
        app = App.__new__(App)
        app.root = Mock(); app.status = Mock(); app.command = Mock(); app.midi_device = Choice('Studio')
        app.events = queue.Queue(); app.midi_dropped = 0; app.midi_activity = MidiActivity()
        app.hardware_midi = MidiControlRouter(); app.mapping = {}; app.learn = None; app.hardware_learn = None
        app.playhead = 0; app.playing = False
        app.street_dispatch = StreetMidiDispatch(app.hardware_midi, MidiAutomationEngine(), app.command, Mock(), Mock())
        app.arm_hardware_learn('BANK PAD 1', 'button')
        event = SimpleNamespace(type='note_on', channel=0, note=36, velocity=100)
        app._enqueue_midi(event); app._poll()
        self.assertEqual(app.midi_activity.count, 1)
        app.command.assert_not_called()
        app._enqueue_midi(event); app._poll()
        self.assertEqual(app.midi_activity.count, 2)
        app.command.assert_called_once_with('BANK PAD 1')


class SharedSetupTests(unittest.TestCase):
    def test_audio_scan_preserves_selected_output_and_running_stream(self):
        app = App.__new__(App); app.audio_device = Choice('1  Studio Interface'); app.status = Mock(); app.engine = Mock()
        devices = [{'name': 'Other', 'max_output_channels': 2}, {'name': 'Studio Interface', 'max_output_channels': 2}]
        with patch.dict(sys.modules, {'sounddevice': SimpleNamespace(query_devices=lambda: devices)}):
            app.scan_audio()
        self.assertEqual(app.audio_device.get(), '1  Studio Interface')
        app.engine.start.assert_not_called(); app.engine.stop.assert_not_called()

    def test_failed_scan_clears_stale_device_choices(self):
        app = App.__new__(App); app.audio_device = Choice('missing device'); app.status = Mock()
        with patch.dict(sys.modules, {'sounddevice': SimpleNamespace(query_devices=Mock(side_effect=OSError('device removed')))}):
            self.assertEqual(app.scan_audio(), [])
        self.assertEqual(app.audio_device.values, [])
        self.assertEqual(app.audio_device.get(), '')

    def test_test_note_requires_explicit_audio_start(self):
        window = AudioMidiWindow.__new__(AudioMidiWindow); window.status = Mock()
        window.app = SimpleNamespace(engine=SimpleNamespace(stream=None), labbs=Mock())
        window.test_note(3, 36)
        window.app.labbs.note_on.assert_not_called()
        self.assertIn('START AUDIO', window.status.set.call_args.args[0])

    def test_test_note_uses_shared_audio_without_editing_patch(self):
        window = AudioMidiWindow.__new__(AudioMidiWindow); window.status = Mock()
        engine = Engine(); engine.stream = object()
        window.app = SimpleNamespace(engine=engine, labbs=engine.labbs)
        before = engine.labbs.serialize()
        window.test_note(3, 36)
        self.assertGreater(max(map(abs, engine.render(1024))), .001)
        self.assertEqual(engine.labbs.serialize(), before)

    def test_closing_setup_does_not_disconnect_or_stop_audio(self):
        window = AudioMidiWindow.__new__(AudioMidiWindow)
        window.win = Mock(); window.app = Mock(); window.poll_id = 'timer'
        window.close()
        window.win.after_cancel.assert_called_once_with('timer')
        window.win.destroy.assert_called_once_with()
        window.app.close_midi.assert_not_called(); window.app.engine.stop.assert_not_called()
