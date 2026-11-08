import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import App
from studio_midi_adapter import MidiControlRouter

class PadLearnTests(unittest.TestCase):
    def app(self):
        app=App.__new__(App);app.hardware_midi=MidiControlRouter();app.hardware_midi.bind('cc',0,8,'PLAY/STOP');app.status=Mock();app.mapping={}
        return app
    def msg(self,n,velocity=100):return SimpleNamespace(type='note_on',channel=0,note=n,velocity=velocity)
    def test_batch_is_staged_and_cancellation_keeps_original_map(self):
        app=self.app();before=app.hardware_midi.serialize();app.arm_pad_learn()
        for n in range(6):self.assertTrue(app._learn_hardware_message(self.msg(40+n)))
        self.assertEqual(app.hardware_midi.serialize(),before)
        app.hardware_learn=None;self.assertEqual(app.hardware_midi.serialize(),before)
    def test_duplicate_messages_and_releases_do_not_advance_batch(self):
        app=self.app();app.arm_pad_learn();app._learn_hardware_message(self.msg(40))
        app._learn_hardware_message(self.msg(40));app._learn_hardware_message(self.msg(40,0))
        self.assertEqual(app.hardware_learn['index'],1)
        self.assertIn('Already captured',app.hardware_status)
    def test_complete_batch_commits_all_pads_in_one_router(self):
        app=self.app();router=app.hardware_midi;app.arm_pad_learn()
        for n in range(16):app._learn_hardware_message(self.msg(40+n))
        self.assertIs(app.hardware_midi,router);self.assertIsNone(app.hardware_learn)
        self.assertEqual(len(router.bindings),17)
        for n in range(16):
            self.assertEqual(router.translate(self.msg(40+n)),[f'BANK PAD {n+1}'])
            self.assertEqual(router.bindings[f'note:0:{40+n}']['control'],f'PAD {n+1}')
