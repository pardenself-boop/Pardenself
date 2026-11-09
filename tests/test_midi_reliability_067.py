import queue
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import App
from street_midi_dispatch import StreetMidiDispatch
from midi_automation_engine import MidiAutomationEngine
from street_midi_queue import MidiPacket
from test_pad_recording_065 import app_fixture


def note(kind='note_on',number=60,velocity=100,channel=0):
    return SimpleNamespace(type=kind,note=number,velocity=velocity,channel=channel)


def instrument_app(capacity=8):
    app=app_fixture();app.recording=False
    app.arr.clips[0].update(kind='labb',labb_index=3,note_pattern='labb-main')
    app.arr.selected={app.arr.clips[0]['id']};app.notes.armed_labb=3
    app.events=queue.Queue(maxsize=capacity);app.midi_dropped=0
    app._midi_note_owners={};app._midi_overflow=threading.Event();app._midi_generation=1
    app.midi_device=Mock();app.midi_device.get.return_value='Maschine Studio'
    app.midi_port=None;app.midi_connected_name=None;app.hardware_learn=None;app.learn=None
    app.street_dispatch=StreetMidiDispatch(app.hardware_midi,MidiAutomationEngine(),app.command,app._midi_note_on,app._midi_note_off,channel_aware=True)
    return app


class NoteLifetimeTests(unittest.TestCase):
    def receive(self,app,event):app.street_dispatch.receive('Studio',event)

    def test_release_after_instrument_switch_targets_original_voice(self):
        app=instrument_app();self.receive(app,note())
        voice=app.labbs.voices[-1]
        app.notes.armed_labb=7;self.receive(app,note('note_off',velocity=0))
        self.assertIsNotNone(voice['release_at']);self.assertEqual(voice['labb'],3)
        self.assertEqual(app._midi_note_owners,{})

    def test_same_pitch_on_two_channels_different_instruments_releases_independently(self):
        app=instrument_app();self.receive(app,note(channel=0))
        app.notes.armed_labb=7;self.receive(app,note(channel=1))
        bass,keys=app.labbs.voices
        self.receive(app,note('note_off',velocity=0,channel=0))
        self.assertIsNotNone(bass['release_at']);self.assertIsNone(keys['release_at'])
        self.receive(app,note('note_off',velocity=0,channel=1))
        self.assertIsNotNone(keys['release_at'])

    def test_unison_same_instrument_waits_for_last_channel_release(self):
        app=instrument_app();self.receive(app,note(channel=0));self.receive(app,note(channel=1))
        self.receive(app,note('note_off',velocity=0,channel=0))
        self.assertTrue(all(v['release_at'] is None for v in app.labbs.voices))
        self.receive(app,note('note_off',velocity=0,channel=1))
        self.assertTrue(all(v['release_at'] is not None for v in app.labbs.voices))

    def test_sustain_keeps_original_instrument_owner(self):
        app=instrument_app();self.receive(app,note())
        self.receive(app,SimpleNamespace(type='control_change',channel=0,control=64,value=127))
        self.receive(app,note('note_off',velocity=0));app.notes.armed_labb=7
        self.assertIsNone(app.labbs.voices[0]['release_at'])
        self.receive(app,SimpleNamespace(type='control_change',channel=0,control=64,value=0))
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])

    def test_orphan_note_off_does_not_cut_mouse_or_sequenced_voice(self):
        app=instrument_app();app.labbs.note_on(60,.8,3)
        self.receive(app,note('note_off',velocity=0))
        self.assertIsNone(app.labbs.voices[0]['release_at'])

    def test_relearning_held_note_as_button_still_releases_original_voice(self):
        app=instrument_app();self.receive(app,note())
        app.hardware_midi.bind('note',0,60,'PLAY/STOP')
        self.receive(app,note('note_off',velocity=0))
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])

    def test_legacy_remap_while_held_does_not_swallow_release(self):
        app=instrument_app();app._enqueue_midi(note());app._poll()
        app.mapping['note_on:0:60']='PLAY/STOP'
        app._enqueue_midi(note('note_on',velocity=0));app._poll()
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])


class InputRecoveryTests(unittest.TestCase):
    def test_callback_snapshot_is_not_changed_by_driver_message_reuse(self):
        app=instrument_app();message=note();app._enqueue_midi(message);message.note=61
        app._poll();self.assertIn((0,60),app._midi_note_owners)
        self.assertNotIn((0,61),app._midi_note_owners)

    def test_overflow_releases_held_notes_and_discards_stale_batch(self):
        app=instrument_app(capacity=2);app._enqueue_midi(note());app._poll()
        app.notes.armed_labb=7
        app._enqueue_midi(note(number=61));app._enqueue_midi(note(number=62))
        app._enqueue_midi(note('note_off',velocity=0));app._poll()
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])
        self.assertEqual(len(app.labbs.voices),1)
        self.assertEqual(app._midi_note_owners,{})
        self.assertIn('overload recovered',app.hardware_status)

    def test_bad_command_does_not_drop_later_note_off_in_same_poll(self):
        app=instrument_app();app._enqueue_midi(note());app._poll()
        app.hardware_midi.bind('cc',0,10,'PAD broken')
        app._enqueue_midi(SimpleNamespace(type='control_change',channel=0,control=10,value=127))
        app._enqueue_midi(note('note_off',velocity=0));app._poll()
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])
        self.assertTrue(any('MIDI message error' in str(call) for call in app.status.config.call_args_list))

    def test_old_generation_packet_is_ignored_after_disconnect(self):
        app=instrument_app();app.close_midi()
        app.events.put_nowait(MidiPacket(1,note()));app._poll()
        self.assertEqual(app.labbs.voices,[])
        app._enqueue_midi(note(),generation=1)
        self.assertTrue(app.events.empty())

    def test_failed_reconnect_invalidates_callback_messages(self):
        app=instrument_app();callbacks=[]
        def fail_open(name,callback):
            callbacks.append(callback);callback(note());raise OSError('busy')
        with patch.dict(sys.modules,{'mido':SimpleNamespace(open_input=fail_open)}),patch('toolboxx.messagebox.showerror'):
            self.assertFalse(app.open_midi())
        callbacks[0](note());app._poll()
        self.assertEqual(app.labbs.voices,[])

    def test_closed_backend_port_releases_notes_without_stopping_transport(self):
        app=instrument_app();app._enqueue_midi(note());app._poll()
        app.midi_port=SimpleNamespace(closed=True,close=Mock());app.midi_connected_name='Studio'
        app._poll()
        self.assertIsNone(app.midi_port);self.assertTrue(app.playing)
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])
        self.assertIn('reconnect',app.hardware_status)

    def test_invalid_legacy_note_values_cannot_trigger_transport(self):
        app=instrument_app();app.mapping['note_on:0:60']='PLAY/STOP'
        app._enqueue_midi(note(velocity=128));app._poll()
        self.assertTrue(app.playing)

    def test_manual_scan_releases_notes_if_connected_input_disappeared(self):
        from unittest.mock import MagicMock
        app=instrument_app();app._enqueue_midi(note());app._poll()
        port=Mock();app.midi_port=port;app.midi_connected_name='Maschine Studio'
        app.midi_device=MagicMock();app.midi_device.get.return_value='Maschine Studio'
        with patch.dict(sys.modules,{'mido':SimpleNamespace(get_input_names=lambda:[])}):app.scan_midi()
        port.close.assert_called_once();self.assertIsNone(app.midi_connected_name)
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])

    def test_channel_panic_is_not_swallowed_by_legacy_mapping(self):
        app=instrument_app();app._enqueue_midi(note());app._poll()
        app.mapping['control_change:0:123']='PLAY/STOP'
        app._enqueue_midi(SimpleNamespace(type='control_change',channel=0,control=123,value=0));app._poll()
        self.assertIsNotNone(app.labbs.voices[0]['release_at'])
        self.assertTrue(app.playing)
