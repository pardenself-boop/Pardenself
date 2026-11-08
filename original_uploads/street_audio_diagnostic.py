"""Offline, dependency-light diagnostic for the TOOLBOXX sound engine.
Does not require a sound card, GUI, or third-party audio libraries.
"""
import argparse
import json
import math
import struct
import sys
import wave
from pathlib import Path

from toolboxx import Engine


def inspect_signal(samples):
    if not samples:
        raise ValueError('Audio engine returned no samples')
    if any(not math.isfinite(x) for x in samples):
        raise ValueError('Audio engine returned NaN or infinity')
    peak = max(abs(x) for x in samples)
    rms = math.sqrt(sum(x*x for x in samples)/len(samples))
    return {'frames':len(samples), 'peak':round(peak,6), 'rms':round(rms,6),
            'clipped_frames':sum(abs(x)>=1.0 for x in samples)}


def run(output_dir, seconds=1.0):
    if not (0.25 <= seconds <= 10):
        raise ValueError('seconds must be between 0.25 and 10')
    folder=Path(output_dir).expanduser().resolve()
    folder.mkdir(parents=True,exist_ok=True)
    e=Engine()
    e.labbs.note_on(note=48,velocity=.85,labb=3,duration=min(.6,seconds*.7))
    total=round(e.sr*seconds)
    samples=[]
    while len(samples)<total:
        samples.extend(e.render(min(512,total-len(samples))))
    metrics=inspect_signal(samples)
    if metrics['peak'] < 0.00001:
        raise RuntimeError('Engine rendered silence: check LABB routing and master gain')
    wav_path=folder/'TOOLBOXX_AUDIO_DIAGNOSTIC.wav'
    with wave.open(str(wav_path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(e.sr)
        # Explicitly clip conversion to prevent invalid PCM integers.
        payload=bytearray()
        for s in samples:
            v=round(max(-1.0,min(1.0,s))*32767)
            payload.extend(struct.pack('<hh',v,v))
        w.writeframes(payload)
    with wave.open(str(wav_path),'rb') as w:
        assert w.getnchannels()==2 and w.getframerate()==e.sr and w.getnframes()==total
    report={'status':'PASS','sample_rate':e.sr,'channels':2,'wav_file':str(wav_path),**metrics,
            'note':'Offline engine test only. Does not prove Windows device playback or MIDI connectivity.'}
    report_path=folder/'TOOLBOXX_AUDIO_DIAGNOSTIC.json'
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description='BOOM BAP TOOLBOXX offline audio engine check')
    parser.add_argument('--output',default=str(Path.home()/'Desktop'/'TOOLBOXX_Sound_Check'))
    parser.add_argument('--seconds',type=float,default=1.0)
    args=parser.parse_args()
    try:
        report=run(args.output,args.seconds)
        print(json.dumps(report,indent=2))
    except Exception as exc:
        print(f'AUDIO CHECK FAILED: {exc}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
