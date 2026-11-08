import json
import queue
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from toolboxx import App, COMMANDS
from studio_midi_adapter import MidiControlRouter
from street_midi_dispatch import StreetMidiDispatch
from midi_automation_engine import MidiAutomationEngine
from project_io import save_project, load_project
from arranger_core import Arranger
from note_lane import NoteLane
from suite_registry import SuiteRouter
from toolboxx import Engine


def app_fixture():
    app=App.__new__(App)
    app.engine=Engine();app.labbs=app.engine.labbs;app.arr=Arranger()
    app.notes=NoteLane();app.suites=SuiteRouter();app.bpm=90
    app.pattern=[[False]*16 for _ in range(32)];app.patterns={'main':app.pattern}
    app.hardware_midi=MidiControlRouter();app.mapping={};app.hardware_learn=None;app.learn=None
    app.midi_port=None;app.midi_connected_name=None;app.hardware_status='Not connected'
    app.events=queue.Queue(maxsize=2048);app.midi_dropped=0
    app.root=Mock();app.status=Mock();app.midi_device=Mock()
    app.midi_device.get.return_value='Maschine Studio Input'
    app.command=Mock();app.playing=False;app.recording=False;app.playhead=0;app.tick_id=None
    app.street_dispatch=StreetMidiDispatch(app.hardware_midi,MidiAutomationEngine(),app.command,Mock(),Mock())
    return app


def note(number=60, velocity=100):
    return SimpleNamespace(type='note_on',channel=0,note=number,velocity=velocity)


class MaschineWorkflowTests(unittest.TestCase):
    def test_learning_consumes_first_message_then_dispatches_next_press(self):
        app=app_fixture();app.mapping['note_on:0:60']='RECORD'
        app.arm_hardware_learn('BANK PAD 1','button')
        app._enqueue_midi(note());app._poll()
        app.command.assert_not_called()
        self.assertIsNone(app.hardware_learn)
        self.assertNotIn('note_on:0:60',app.mapping)
        app._enqueue_midi(note());app._poll()
        app.command.assert_called_once_with('BANK PAD 1')
        app._enqueue_midi(note(velocity=0));app._poll()
        self.assertEqual(app.command.call_count,1)

    def test_encoder_learning_ignores_notes_and_keeps_relative_mode(self):
        app=app_fixture();app.arm_hardware_learn('HW JOG','relative_twos_complement')
        self.assertFalse(app._learn_hardware_message(note()))
        cc=SimpleNamespace(type='control_change',channel=3,control=12,value=1)
        self.assertTrue(app._learn_hardware_message(cc))
        self.assertEqual(app.hardware_midi.translate(cc),['HW JOG +'])
        cc.value=127
        self.assertEqual(app.hardware_midi.translate(cc),['HW JOG -'])

    def test_button_release_does_not_complete_learning(self):
        app=app_fixture();app.arm_hardware_learn('PLAY/STOP','button')
        self.assertFalse(app._learn_hardware_message(note(velocity=0)))
        self.assertIsNotNone(app.hardware_learn)
        self.assertEqual(app.hardware_midi.bindings,{})

    def test_controller_mapping_round_trip_keeps_dispatcher_reference(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'song.json';app=app_fixture()
            app.hardware_midi.bind('note',0,60,'BANK PAD 1')
            app.hardware_midi.bind('cc',1,9,'HW JOG','relative_binary_offset')
            save_project(app,path)
            restored=app_fixture();router=restored.hardware_midi
            load_project(restored,path)
            self.assertIs(restored.hardware_midi,router)
            self.assertIs(restored.street_dispatch.router,router)
            self.assertEqual(router.serialize(),app.hardware_midi.serialize())
            restored.street_dispatch.receive('Maschine Studio',note())
            restored.command.assert_called_once_with('BANK PAD 1')

    def test_corrupt_controller_data_leaves_project_and_mappings_intact(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'song.json';app=app_fixture()
            app.hardware_midi.bind('note',0,60,'PLAY/STOP');save_project(app,path)
            data=json.loads(path.read_text());data['controller']['bindings']['cc:0:2']={'command':'JOG','mode':'broken'}
            path.write_text(json.dumps(data));before=app.arr
            with self.assertRaises(ValueError):load_project(app,path)
            self.assertIs(app.arr,before)
            self.assertEqual(len(app.hardware_midi.bindings),1)

    def test_old_project_keeps_existing_hardware_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'song.json';app=app_fixture();save_project(app,path)
            data=json.loads(path.read_text());data.pop('controller');path.write_text(json.dumps(data))
            app.hardware_midi.bind('note',0,60,'PLAY/STOP');load_project(app,path)
            self.assertEqual(app.hardware_midi.translate(note()),['PLAY/STOP'])

    def test_failed_reconnect_clears_closed_port(self):
        app=app_fixture();old=Mock();app.midi_port=old
        backend=SimpleNamespace(open_input=Mock(side_effect=RuntimeError('Port busy')))
        with patch.dict(sys.modules,{'mido':backend}),patch('toolboxx.messagebox.showerror'):
            self.assertFalse(app.open_midi())
        old.close.assert_called_once()
        self.assertIsNone(app.midi_port)
        self.assertIsNone(app.midi_connected_name)
        self.assertIn('Port busy',app.hardware_status)

    def test_scan_prefers_studio_without_connecting(self):
        app=app_fixture();app.midi_device.get.return_value=''
        # Combobox uses mapping assignment in addition to set/get.
        from unittest.mock import MagicMock
        app.midi_device=MagicMock();app.midi_device.get.return_value=''
        backend=SimpleNamespace(get_input_names=lambda:['Other Input','NI Maschine Studio MIDI'])
        with patch.dict(sys.modules,{'mido':backend}):names=app.scan_midi()
        self.assertEqual(len(names),2)
        app.midi_device.set.assert_called_once_with('NI Maschine Studio MIDI')
        self.assertIsNone(app.midi_port)

    def test_invalid_profile_cannot_partially_replace_good_bindings(self):
        router=MidiControlRouter();router.bind('note',0,60,'PLAY/STOP')
        with self.assertRaises(ValueError):
            router.deserialize({'schema':1,'bindings':{'cc:0:1':{'command':'JOG','mode':'relative_binary_offset'},'bad':[]}})
        self.assertEqual(router.translate(note()),['PLAY/STOP'])

    def test_bank_pad_commands_follow_bank_and_preserve_absolute_commands(self):
        app=app_fixture();app.command=App.command.__get__(app)
        app._refresh=Mock();app.bank=0;app.selected_pad=0
        with patch.object(app.engine,'trigger') as trigger:
            app.command('BANK PAD 1');app.command('BANK NEXT');app.command('BANK PAD 1')
            self.assertEqual([c.args[0] for c in trigger.call_args_list],[0,16])
            self.assertEqual(app.selected_pad,16)
            app.command('PAD 1');self.assertEqual(app.selected_pad,0)
        self.assertTrue(all(f'BANK PAD {i}' in COMMANDS for i in range(1,17)))
