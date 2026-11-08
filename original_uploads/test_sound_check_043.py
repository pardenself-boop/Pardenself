import os, tempfile, unittest, wave, struct
from toolboxx import Engine

class SoundCheckIntegration(unittest.TestCase):
    def test_loaded_sample_reaches_master_engine(self):
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,'kick.wav')
            with wave.open(path,'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000)
                w.writeframes(b''.join(struct.pack('<h',int(12000*(1-i/1000))) for i in range(1000)))
            e=Engine();e.labbs.crate.load(3,path,root_note=60)
            e.labbs.note_on(note=60,velocity=1,labb=3,duration=2)
            samples=e.render(512)
            self.assertTrue(any(abs(x)>0.001 for x in samples))
            e.labbs.note_off(note=60,labb=3)
            for _ in range(8):e.render(512)
            self.assertFalse(e.labbs.crate.voices)
