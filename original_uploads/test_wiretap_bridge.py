import sys, unittest, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from studio_midi_adapter import MidiControlRouter
class Msg:
 def __init__(self,typ='control_change',channel=0,control=10,value=1):
  self.type=typ;self.channel=channel;self.control=control;self.value=value
class BridgeTests(unittest.TestCase):
 def test_profile_compatible(self):
  a=MidiControlRouter();a.bind('cc',0,10,'HW JOG','relative_twos_complement')
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'mapping.json';a.save(path);b=MidiControlRouter();b.load(path)
   self.assertEqual(b.translate(Msg(value=1)),['HW JOG +'])
   self.assertEqual(b.translate(Msg(value=127)),['HW JOG -'])
 def test_button_zero_ignored(self):
  a=MidiControlRouter();a.bind('cc',0,10,'PLAY/STOP')
  self.assertEqual(a.translate(Msg(value=0)),[])
  self.assertEqual(a.translate(Msg(value=127)),['PLAY/STOP'])
if __name__=='__main__':unittest.main()
