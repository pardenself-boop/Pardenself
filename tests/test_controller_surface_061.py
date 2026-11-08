import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from controller_surface import CONTROLS,BY_KEY,hit_test,move_rect
from studio_midi_adapter import MidiControlRouter

class SurfaceTests(unittest.TestCase):
    def test_every_physical_control_has_unique_clickable_hotspot(self):
        self.assertEqual(len(CONTROLS),len(BY_KEY))
        for control in CONTROLS:
            if control.key=='JOG ROTATE':continue
            x0,y0,x1,y1=control.rect
            self.assertEqual(hit_test((x0+x1)/2,(y0+y1)/2),control.key,control.key)
    def test_pad_layout_matches_bottom_left_pad_one(self):
        self.assertGreater(BY_KEY['PAD 1'].rect[1],BY_KEY['PAD 13'].rect[1])
        self.assertLess(BY_KEY['PAD 1'].rect[0],BY_KEY['PAD 4'].rect[0])
    def test_hotspots_and_physical_bindings_survive_profile_save(self):
        router=MidiControlRouter();router.bind('note',0,60,'BANK PAD 1','button','PAD 1')
        router.surface_layout['PAD 1']=move_rect(BY_KEY['PAD 1'].rect,.01,.02)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'map.json';router.save(path);restored=MidiControlRouter();restored.load(path)
        self.assertEqual(restored.serialize(),router.serialize())
        self.assertEqual(restored.translate(SimpleNamespace(type='note_on',channel=0,note=60,velocity=100)),['BANK PAD 1'])
    def test_relearning_one_control_replaces_its_old_address(self):
        router=MidiControlRouter();router.bind('note',0,60,'BANK PAD 1',control='PAD 1')
        router.bind('note',0,61,'BANK PAD 1',control='PAD 1')
        self.assertEqual(list(router.bindings),['note:0:61'])
    def test_corrupt_layout_does_not_replace_existing_mapping(self):
        router=MidiControlRouter();router.bind('note',0,60,'PLAY/STOP')
        with self.assertRaises(ValueError):router.deserialize({'schema':1,'bindings':{},'surface_layout':{'PAD 1':[0,0,-1,1]}})
        self.assertEqual(len(router.bindings),1)
    def test_hotspot_drag_clamps_to_image_bounds(self):
        rect=BY_KEY['PAD 1'].rect;moved=move_rect(rect,5,-5)
        self.assertEqual(moved[2],1);self.assertEqual(moved[1],0)
        self.assertAlmostEqual(moved[2]-moved[0],rect[2]-rect[0])
    def test_loop_encoder_moves_in_both_directions(self):
        router=MidiControlRouter();router.bind('cc',0,1,'LOOP MOVE +','relative_twos_complement','KNOB 1')
        msg=SimpleNamespace(type='control_change',channel=0,control=1,value=1)
        self.assertEqual(router.translate(msg),['LOOP MOVE +']);msg.value=127
        self.assertEqual(router.translate(msg),['LOOP MOVE -'])
