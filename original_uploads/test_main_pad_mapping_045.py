import os,sys,unittest
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','app'))
from toolboxx import App, COMMANDS

class MainPadMappingTests(unittest.TestCase):
 def make_app(self):
  app=App.__new__(App)
  app.bank=0;app.selected_pad=0
  app.engine=SimpleNamespace(trigger=Mock())
  app._refresh=Mock()
  return app
 def test_all_32_midi_learn_commands_exist(self):
  self.assertTrue(all(f'PAD {n}' in COMMANDS for n in range(1,33)))
 def test_absolute_pad_command_does_not_wrap(self):
  app=self.make_app()
  for n in range(1,33):
   app.command(f'PAD {n}')
   self.assertEqual(app.selected_pad,n-1)
   self.assertEqual(app.bank,(n-1)//16)
  self.assertEqual([c.args[0] for c in app.engine.trigger.call_args_list],list(range(32)))
 def test_visible_pad_respects_bank(self):
  app=self.make_app();app.bank=1
  app.pad(15)
  self.assertEqual(app.selected_pad,31)
  app.engine.trigger.assert_called_once_with(31)
 def test_main_midi_notes_map_36_through_67(self):
  app=self.make_app();app.arr=SimpleNamespace(selected=set(),clips=[])
  for n in range(36,68):app._midi_note_on(n,.9)
  self.assertEqual([c.args[0] for c in app.engine.trigger.call_args_list],list(range(32)))
 def test_out_of_range_rejected(self):
  app=self.make_app()
  for n in (-1,32):
   with self.assertRaises(ValueError):app.trigger_absolute_pad(n)
  app.engine.trigger.assert_not_called()

if __name__=='__main__':unittest.main()
