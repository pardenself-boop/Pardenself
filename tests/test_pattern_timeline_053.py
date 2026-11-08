import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from street_song_bounce import expand_patterns

class PatternTimelineTests(unittest.TestCase):
    def setUp(self):
        self.song = {'bpm': 85, 'bars': 4, 'samples': {'1': 'kick.wav'},
                     'patterns': {'beat': {'steps': 16, 'events': [{'pad': 1, 'step': 0}, {'pad': 1, 'step': 8}]}},
                     'clips': [{'pattern': 'beat', 'bar': 0, 'repeats': 4}]}
    def test_four_bar_expansion(self):
        hits = expand_patterns(self.song)
        self.assertEqual(len(hits), 8)
        self.assertEqual([h['beat'] for h in hits], [0, 2, 4, 6, 8, 10, 12, 14])
    def test_explicit_hits_remain(self):
        self.song['hits'] = [{'pad': 1, 'beat': 1}]
        self.assertEqual(len(expand_patterns(self.song)), 9)
    def test_rejects_missing_pattern(self):
        self.song['clips'][0]['pattern'] = 'missing'
        with self.assertRaises(ValueError): expand_patterns(self.song)
    def test_rejects_invalid_step(self):
        self.song['patterns']['beat']['events'][0]['step'] = 16
        with self.assertRaises(ValueError): expand_patterns(self.song)
    def test_rejects_out_of_song_clip(self):
        self.song['clips'][0]['bar'] = 2
        with self.assertRaises(ValueError): expand_patterns(self.song)
    def test_rejects_excessive_repeats(self):
        self.song['clips'][0]['repeats'] = 1000
        with self.assertRaises(ValueError): expand_patterns(self.song)
