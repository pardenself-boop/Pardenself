import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from street_midi_queue import StreetMidiQueue

class FakeDispatch:
    def __init__(self):
        self.calls=[]
    def receive(self, device, message, position=0, playing=False):
        self.calls.append((device,message.type,message.note,position,playing))
        return message.type
    def panic(self):
        self.calls.append(('panic',))

class QueueTests(unittest.TestCase):
    def test_order_and_snapshot(self):
        d=FakeDispatch(); q=StreetMidiQueue(d)
        m=SimpleNamespace(type='note_on',note=60,velocity=127,channel=0)
        q.submit('Maschine',m); m.note=61
        q.submit('Maschine',SimpleNamespace(type='note_off',note=60,velocity=0))
        self.assertEqual(q.drain(position=42,playing=True),['note_on','note_off'])
        self.assertEqual([x[2] for x in d.calls],[60,60])
    def test_bounded_drain(self):
        d=FakeDispatch(); q=StreetMidiQueue(d,capacity=4)
        for i in range(3): q.submit('x',SimpleNamespace(type='note_on',note=i))
        q.drain(max_events=2)
        self.assertEqual(q.pending(),1)
    def test_overflow_panic(self):
        d=FakeDispatch(); q=StreetMidiQueue(d,capacity=2)
        for i in range(3): q.submit('x',SimpleNamespace(type='note_on',note=i))
        q.drain()
        self.assertEqual(d.calls[0],('panic',))
        self.assertEqual([x[2] for x in d.calls[1:]],[2])
        self.assertEqual(q.overflow_panics,1)
    def test_unsupported(self):
        d=FakeDispatch(); q=StreetMidiQueue(d)
        self.assertFalse(q.submit('x',SimpleNamespace(type='clock')))
        self.assertEqual(q.pending(),0)

if __name__=='__main__': unittest.main()
