import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from street_audio_diagnostic import run,inspect_signal

class TestAudioDiagnostic(unittest.TestCase):
    def test_wav_and_report(self):
        with tempfile.TemporaryDirectory() as folder:
            report=run(folder,.25)
            self.assertEqual(report['status'],'PASS')
            self.assertGreater(report['peak'],0)
            self.assertEqual(report['frames'],12000)
            with wave.open(report['wav_file'],'rb') as w:
                self.assertEqual(w.getnframes(),12000)
                self.assertEqual(w.getnchannels(),2)
            self.assertTrue((Path(folder)/'TOOLBOXX_AUDIO_DIAGNOSTIC.json').exists())
    def test_rejects_nonfinite(self):
        with self.assertRaises(ValueError):inspect_signal([0,float('nan')])
    def test_rejects_empty(self):
        with self.assertRaises(ValueError):inspect_signal([])
    def test_rejects_invalid_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):run(folder,0)

if __name__=='__main__':unittest.main()
