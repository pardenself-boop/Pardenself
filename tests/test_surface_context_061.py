import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from surface_context import SurfaceContext
from toolboxx import Engine
from arranger_core import Arranger
from arranger_ranges import RangeEditor
from hardware_edit import HardwareEdit

class ContextTests(unittest.TestCase):
    def app(self):
        engine=Engine();app=SimpleNamespace(engine=engine,labbs=engine.labbs,mix_rack=engine.mix_rack,arr=Arranger(),playhead=0,_refresh=Mock(),command=Mock(),status=Mock(),notes=SimpleNamespace(armed_labb=0))
        app.range_editor=RangeEditor(app.arr);app.hardware_edit=HardwareEdit(app);return app
    def test_same_soft_key_changes_by_context(self):
        app=self.app();context=SurfaceContext(app)
        context.key(0);app.command.assert_called_with('MODE MRQ')
        context.set_page('FX');context.key(0);app.command.assert_called_with('FX ADD eq')
        context.set_page('SOUND');context.key(0);app.command.assert_called_with('LABB PREV')
    def test_sound_knob_changes_real_selected_instrument(self):
        app=self.app();context=SurfaceContext(app);context.set_page('SOUND');before=app.labbs.parameters[0]['cutoff']
        context.knob(5,-1);self.assertLess(app.labbs.parameters[0]['cutoff'],before)
    def test_fx_knob_changes_real_chain_parameters(self):
        app=self.app();module=app.mix_rack.add('eq');context=SurfaceContext(app);context.set_page('FX');context.knob(0,1)
        self.assertGreater(module.params['low_gain_db'],0)
    def test_arrange_knobs_edit_loop_and_preview_clip_edit(self):
        app=self.app();context=SurfaceContext(app);context.knob(0,1);self.assertEqual(app.arr.loop_start,.25)
        before=app.arr.clips[0]['start'];context.knob(5,1)
        self.assertEqual(app.arr.clips[0]['start'],before);self.assertEqual(app.hardware_edit.operation,'MOVE')
        app.hardware_edit.click();self.assertGreater(app.arr.clips[0]['start'],before)
    def test_own_bank_applies_real_patch_and_arms_instrument(self):
        app=self.app();context=SurfaceContext(app);context.choose_sound(1)
        self.assertEqual(app.labbs.selected,7);self.assertEqual(app.notes.armed_labb,7)
