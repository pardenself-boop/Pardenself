import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from audio_smoke_test import AudioTest
class MidiBridgeTests(unittest.TestCase):
 def test_queue_accepts_note(self):
  import queue
  x=AudioTest.__new__(AudioTest);x.midi_events=queue.Queue(maxsize=2)
  x.enqueue_midi(('note',1));self.assertEqual(x.midi_events.get_nowait(),('note',1))
 def test_overflow_sends_panic(self):
  import queue
  x=AudioTest.__new__(AudioTest);x.midi_events=queue.Queue(maxsize=1)
  x.enqueue_midi('old');x.enqueue_midi('new');self.assertEqual(x.midi_events.get_nowait(),('panic',))
if __name__=='__main__':unittest.main()
