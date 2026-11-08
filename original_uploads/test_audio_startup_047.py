import sys, unittest, types
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import Engine

class FakeStream:
    instances=[]
    fail=False
    def __init__(self,**kwargs):
        self.kwargs=kwargs;self.closed=False;self.stopped=False
        self.instances.append(self)
    def start(self):
        if self.fail:raise OSError('device busy')
    def stop(self):self.stopped=True
    def close(self):self.closed=True

class TestAudioStartup(unittest.TestCase):
    def setUp(self):FakeStream.instances=[];FakeStream.fail=False
    def test_starts_and_stops_default_device(self):
        with patch.dict(sys.modules,{'sounddevice':types.SimpleNamespace(OutputStream=FakeStream)}):
            e=Engine();e.start();self.assertIsNotNone(e.stream)
            self.assertIsNone(e.stream.kwargs['device']);e.stop()
            self.assertTrue(FakeStream.instances[0].closed)
            self.assertIsNone(e.stream)
    def test_failed_start_closes_stream_and_allows_retry(self):
        with patch.dict(sys.modules,{'sounddevice':types.SimpleNamespace(OutputStream=FakeStream)}):
            e=Engine();FakeStream.fail=True
            with self.assertRaisesRegex(RuntimeError,'device busy'):e.start(3)
            self.assertTrue(FakeStream.instances[0].closed)
            self.assertIsNone(e.stream)
            FakeStream.fail=False;e.start(3)
            self.assertEqual(e.stream.kwargs['device'],3);e.stop()
    def test_callback_silences_on_render_failure(self):
        with patch.dict(sys.modules,{'sounddevice':types.SimpleNamespace(OutputStream=FakeStream)}):
            e=Engine();e.start()
            class Output:
                def __init__(self):self.data=[[1,1] for _ in range(4)]
                def fill(self,n):self.data=[[n,n] for _ in self.data]
                def __getitem__(self,i):return self.data[i]
            o=Output()
            e.render=lambda n: (_ for _ in ()).throw(ValueError('bad DSP'))
            e.stream.kwargs['callback'](o,4,None,None)
            self.assertEqual(o.data,[[0,0]]*4)
            self.assertIn('bad DSP',e.audio_status)
            e.stop()
if __name__=='__main__':unittest.main()
