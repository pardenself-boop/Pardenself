import sys,unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from studio_midi_adapter import MidiControlRouter
from midi_automation_engine import MidiAutomationEngine
from street_midi_dispatch import StreetMidiDispatch
class Tests(unittest.TestCase):
 def setUp(self):
  self.commands=[];self.notes=[];self.changes=[]
  self.router=MidiControlRouter();self.automation=MidiAutomationEngine()
  self.dispatch=StreetMidiDispatch(self.router,self.automation,self.commands.append,lambda n,v:self.notes.append(('on',n,v)),lambda n:self.notes.append(('off',n)),self.changes.extend)
 def test_mapped_note_does_not_play(self):
  self.router.bind('note',0,36,'PLAY/STOP')
  self.dispatch.receive('Maschine',SimpleNamespace(type='note_on',channel=0,note=36,velocity=100))
  self.dispatch.receive('Maschine',SimpleNamespace(type='note_off',channel=0,note=36,velocity=0))
  self.assertEqual(self.commands,['PLAY/STOP']);self.assertEqual(self.notes,[])
 def test_unmapped_note_on_and_off(self):
  self.dispatch.receive('Maschine',SimpleNamespace(type='note_on',channel=0,note=60,velocity=127))
  self.dispatch.receive('Maschine',SimpleNamespace(type='note_on',channel=0,note=60,velocity=0))
  self.assertEqual(self.notes,[('on',60,1.0),('off',60)])
 def test_encoder_dispatch(self):
  self.router.bind('cc',0,10,'HW JOG','relative_twos_complement')
  self.dispatch.receive('Maschine',SimpleNamespace(type='control_change',channel=0,control=10,value=2))
  self.assertEqual(self.commands,['HW JOG +','HW JOG +'])
 def test_automation_reaches_parameter_callback(self):
  self.automation.bind('Maschine','cc',0,11,'mix.gain',scope='global')
  self.dispatch.receive('Maschine',SimpleNamespace(type='control_change',channel=0,control=11,value=127))
  self.assertEqual(self.changes[0][0],'mix.gain')
if __name__=='__main__':unittest.main()
