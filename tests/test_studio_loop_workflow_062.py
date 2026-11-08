"""Studio manual 13.3.14.2: dedicated loop-page control positions."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from surface_context import SurfaceContext
from arranger_core import Arranger
from controller_surface import BY_KEY
from toolboxx import App,COMMANDS


class StudioLoopWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.app=SimpleNamespace(arr=Arranger(),labbs=SimpleNamespace(selected=0),_refresh=Mock())
        self.app.surface_context=SurfaceContext(self.app)
        self.app.command=lambda command:App.command(self.app,command)
        self.app.surface_context.set_page('LOOP')

    def test_manual_knob_positions_and_undo(self):
        context=self.app.surface_context
        start,end=self.app.arr.loop_start,self.app.arr.loop_end
        context.knob(0,1)
        self.assertEqual((self.app.arr.loop_start,self.app.arr.loop_end),(start+.25,end+.25))
        context.knob(2,1)
        self.assertEqual(self.app.arr.loop_start,start+.5)
        context.knob(3,1)
        self.assertEqual(self.app.arr.loop_end,end+.5)
        self.app.arr.undo()
        self.assertEqual(self.app.arr.loop_end,end+.25)
        self.assertEqual([context.values()[i][0] for i in (0,2,3)],['POSITION','START','LENGTH'])

    def test_unused_knobs_do_not_edit_arrangement(self):
        before=self.app.arr.serialize()
        for index in (1,4,5,6,7):self.app.surface_context.knob(index,1)
        self.assertEqual(self.app.arr.serialize(),before)

    def test_buttons_four_and_five_control_whole_song_and_loop(self):
        self.app.arr.loop_start=4
        self.app.surface_context.key(3)
        self.assertEqual(self.app.arr.loop_start,0)
        self.assertEqual(self.app.arr.loop_end,max(c['start']+c['length'] for c in self.app.arr.clips))
        before=self.app.arr.loop_enabled
        self.app.surface_context.key(4)
        self.assertEqual(self.app.arr.loop_enabled,not before)

    def test_loop_page_is_available_to_midi_learn(self):
        self.assertIn('SURFACE LOOP',COMMANDS)
        self.app.surface_context.key(0)
        self.assertEqual(self.app.surface_context.page,'ARRANGE')

    def test_navigation_defaults_target_toolboxx_contexts(self):
        expected={'PLUGIN':'EDIT SOUND','BROWSE':'BROWSE SOUNDS','MIX':'EDIT FX','ARRANGE':'SURFACE ARRANGE'}
        for key,command in expected.items():self.assertEqual(BY_KEY[key].command,command)
