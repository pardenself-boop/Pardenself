import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import App,Engine
from studio_midi_adapter import MidiControlRouter
from midi_automation_engine import MidiAutomationEngine
from street_midi_dispatch import StreetMidiDispatch


class PadVelocityTests(unittest.TestCase):
    def engine(self):
        engine=Engine()
        engine.samples[0]=([.1]*1024,48000,'velocity test')
        return engine

    def test_soft_hit_is_quieter_across_render_blocks(self):
        soft,loud=self.engine(),self.engine()
        soft.trigger(0,.25);loud.trigger(0,1.)
        for _ in range(2):
            a,b=soft.render(64),loud.render(64)
            self.assertGreater(max(a),0)
            self.assertLess(max(a),max(b)*.4)

    def test_zero_and_invalid_velocities_do_not_create_voices(self):
        engine=self.engine();engine.trigger(0,0)
        for velocity in (-1,1.1,float('nan'),float('inf'),True,'loud'):
            with self.subTest(velocity=velocity):
                with self.assertRaises(ValueError):engine.trigger(0,velocity)
        self.assertEqual(engine.voices,[])

    def test_overlapping_hits_keep_independent_strength(self):
        engine=self.engine();engine.trigger(0,.2);engine.trigger(0,.8)
        engine.render(32)
        self.assertEqual([voice[2] for voice in engine.voices],[.2,.8])

    def test_learned_banked_pad_reaches_real_engine_with_velocity(self):
        app=App.__new__(App);app.engine=self.engine();app.engine.samples[31]=app.engine.samples[0]
        app.bank=1;app.selected_pad=16;app._refresh=Mock()
        router=MidiControlRouter();router.bind('note',2,47,'BANK PAD 16',control='PAD 16')
        ordinary=Mock();note_on=Mock();note_off=Mock()
        dispatcher=StreetMidiDispatch(router,MidiAutomationEngine(),ordinary,note_on,note_off,pad_command=app._midi_pad_command)
        for kind,velocity in [('note_on',32),('note_off',64),('note_on',0)]:
            dispatcher.receive('Maschine Studio',SimpleNamespace(type=kind,channel=2,note=47,velocity=velocity))
        self.assertEqual(app.selected_pad,31)
        self.assertEqual(len(app.engine.voices),1)
        self.assertAlmostEqual(app.engine.voices[0][2],32/127)
        ordinary.assert_not_called();note_on.assert_not_called();note_off.assert_not_called()

    def test_unmapped_pad_note_preserves_velocity(self):
        app=App.__new__(App);app.arr=SimpleNamespace(selected=set(),clips=[])
        app.engine=self.engine();app.bank=0;app._refresh=Mock()
        app._midi_note_on(36,.4)
        self.assertEqual(app.engine.voices[0][2],.4)

    def test_invalid_mapped_notes_cannot_trigger_commands(self):
        router=MidiControlRouter();router.bind('note',0,36,'PAD 1')
        action=Mock();pad=Mock()
        dispatcher=StreetMidiDispatch(router,MidiAutomationEngine(),action,Mock(),Mock(),pad_command=pad)
        for velocity in (-1,128,True,float('nan')):
            dispatcher.receive('Studio',SimpleNamespace(type='note_on',channel=0,note=36,velocity=velocity))
        action.assert_not_called();pad.assert_not_called()
