"""Regression tests for simultaneous Track City events and malformed tempo."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from track_city_bounce import TrackCityRender, bounce_track_city

class FakeEngine:
    sr = 48000
    def __init__(self):
        self.regions = SimpleNamespace(start=lambda *a, **k: None)
        self.labbs = SimpleNamespace(note_on=lambda *a: None)
        self.samples = [None] * 32
    def render(self, frames):
        return [0.0] * frames
    def trigger(self, pad):
        pass

class TrackCitySchedule057(unittest.TestCase):
    def test_simultaneous_audio_regions(self):
        engine = FakeEngine()
        clips = [{'start':0,'path':'a.wav'}, {'start':0,'path':'b.wav'}]
        renderer = TrackCityRender(engine, [], 90, clips)
        self.assertEqual(len(renderer.render(128)),128)
        self.assertEqual(renderer.next_audio,2)
    def test_simultaneous_midi_notes(self):
        engine = FakeEngine()
        notes = [{'beat':0,'pitch':40,'velocity':.8,'labb':3,'duration':1},
                 {'beat':0,'pitch':43,'velocity':.8,'labb':3,'duration':1}]
        renderer = TrackCityRender(engine, [], 90, [], notes)
        self.assertEqual(len(renderer.render(128)),128)
        self.assertEqual(renderer.next_midi,2)
    def test_invalid_tempo_rejected_before_division(self):
        arranger=SimpleNamespace(clips=[])
        for tempo in (0, -1, float('nan'), float('inf'), True):
            with self.subTest(tempo=tempo), self.assertRaises(ValueError):
                bounce_track_city(FakeEngine(), arranger, {}, tempo, 'out.wav', bars=1)

if __name__=='__main__': unittest.main()
