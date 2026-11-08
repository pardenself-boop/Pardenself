import math
import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from mix_rack import MixRack
from toolboxx import Engine
from arranger_core import Arranger
from note_lane import NoteLane
from track_city_bounce import bounce_track_city

class StreetFXTests(unittest.TestCase):
    def test_empty_bypassed_and_hidden_have_correct_audio_semantics(self):
        values=[-.5,0,.5];rack=MixRack();self.assertEqual(rack.process(values),values)
        clip=rack.add('clipper');clip.params['ceiling_db']=-12
        rack.bypass(0);self.assertEqual(rack.process(values),values)
        rack.bypass(0,False);rack.hide(0)
        self.assertLess(max(rack.process(values)),.3)
    def test_clipper_enforces_ceiling_and_dry_mix(self):
        rack=MixRack();module=rack.add('clipper');module.params.update(ceiling_db=-6,drive_db=12,mix=1)
        out=rack.process([-.9,.1,.9]);self.assertLessEqual(max(abs(x) for x in out),10**(-6/20))
        module.params['mix']=0;self.assertEqual(rack.process([-.9,.9]),[-.9,.9])
    def test_density_has_audible_effect_and_zero_amount_is_transparent(self):
        rack=MixRack();module=rack.add('density');module.params['amount']=0
        self.assertEqual(rack.process([-.2,.2]),[-.2,.2])
        module.params['amount']=.7;self.assertGreater(rack.process([.1])[0],.1)
    def test_eq_boosts_low_frequency_and_flat_is_transparent(self):
        values=[.1*math.sin(2*math.pi*60*i/48000) for i in range(4000)]
        rack=MixRack();module=rack.add('eq');self.assertEqual(rack.process(values),values)
        module.params['low_gain_db']=12;out=rack.process(values)
        self.assertGreater(sum(v*v for v in out[1000:]),sum(v*v for v in values[1000:])*4)
    def test_compressor_reduces_sustained_peak(self):
        rack=MixRack();module=rack.add('compressor');module.params.update(threshold_db=-24,ratio=8,attack_ms=.1)
        out=rack.process([.5]*1000)
        self.assertLess(out[-1],.15)
    def test_filter_and_compressor_state_survive_block_boundaries(self):
        rack=MixRack();rack.add('eq').params['high_gain_db']=-4;rack.add('compressor')
        other=MixRack.from_json(rack.to_json());values=[math.sin(i*.05)*.5 for i in range(2000)]
        whole=rack.process(values);split=other.process(values[:333])+other.process(values[333:])
        self.assertEqual(whole,split)
    def test_engine_master_rack_reaches_output(self):
        dry=Engine();wet=Engine()
        for engine in (dry,wet):engine.samples[0]=([.8]*512,48000,'test');engine.trigger(0)
        wet.mix_rack.add('clipper').params['ceiling_db']=-12
        self.assertLess(max(wet.render(256)),max(dry.render(256)))
    def test_track_city_bounce_restores_instrument_mute_and_fx(self):
        engine=Engine();engine.labbs.mute[3]=True;engine.mix_rack.add('density')
        arr=Arranger();arr.clips=[dict(id='bass',kind='labb',track=0,start=0,length=4,offset=0,labb_index=3,note_pattern='labb-main')]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'out.wav';bounce_track_city(engine,arr,{},120,path,bars=1,note_lane=NoteLane())
            with wave.open(str(path),'rb') as stream:self.assertFalse(any(stream.readframes(96000)))

    def test_project_recalls_rack_order_parameters_and_engine_alias(self):
        from test_project_ui_059 import session
        from project_io import save_project,load_project
        app=session();app.engine.mix_rack.add('density').params['amount']=.7;app.engine.mix_rack.add('eq').params['low_gain_db']=-3
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'project.json';save_project(app,path);restored=session();load_project(restored,path)
        self.assertIs(restored.mix_rack,restored.engine.mix_rack)
        self.assertEqual(restored.mix_rack.to_json(),app.engine.mix_rack.to_json())
    def test_bounce_uses_rack_without_consuming_live_voices(self):
        engine=Engine();engine.samples[0]=([.15]*512,48000,'test');engine.trigger(0)
        arr=Arranger();arr.clips=[dict(id='drum',kind='pattern',track=0,start=0,length=4,offset=0,pattern_id='main')]
        pattern=[[False]*16 for _ in range(32)];pattern[0][0]=True
        with tempfile.TemporaryDirectory() as folder:
            dry=Path(folder)/'dry.wav';wet=Path(folder)/'wet.wav'
            bounce_track_city(engine,arr,{'main':pattern},120,dry,bars=1)
            engine.mix_rack.add('density').params['amount']=.8
            bounce_track_city(engine,arr,{'main':pattern},120,wet,bars=1)
            self.assertNotEqual(dry.read_bytes(),wet.read_bytes())
        self.assertEqual(engine.voices,[[0,0.0,1.0]])
